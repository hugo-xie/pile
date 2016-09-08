/*jslint browser: true*/
/*global
    intelhex, hex_md5, $
*/

var image = {};

$.fn.extend({
  enable: function() {
    return this.each(function() {
      $(this).prop('disabled', false);
    });
  },
  disable: function() {
    return this.each(function() {
      $(this).prop('disabled', true);
    });
  }
});

var readLeInt = function(data) {
    var i, ans;
    for (i=0, ans=0; i < data.length; ++i) {
        ans |= (0xff & data[i]) << (i * 8);
    }
    return ans;
};

var setError = function(err) {
    $("#errorMessage").text(err.toString());
    if (err.toString()) {
        $("#alertBox").show(100);
    } else {
        $("#alertBox").hide();
    }
};

var hexify = function(i, bytes) {
    return "0x" + ("00000000000000000000000" + i.toString(16)).substr(-(bytes*2));
};

var initImage = function() {
    image.currentBase = 0;
    image.version = null;
    image.base = null;
    image.md5sum = null;
    image.base64value = "";
    image.binary = "";
    image.binarybase64value = "";
    image.binarymd5sum = "";
};

var resetUi = function(includeFilePicker) {
    setError("");
    $('#basicInfo').hide();
    $('#progressBar').parent().hide();
    $('#infoBox').hide();
    $('#buttons').hide();
    $('#successMessage').text('');
    $('#btnUpload').enable().show();
    $('#btnReset').enable().show();
    $('#btnCancel').enable().hide();
    if (includeFilePicker) {
        $('#filePicker').val("");
    }
};

var reset = function() {
    initImage();
    resetUi(true);
};

var fillInfo = function(image) {
    // document.getElementById("base64textarea").value = image.base64value;
    if (image.version === null) {
        throw new Error("no version information found in the hex file.");
    }
    if (image.base === null) {
        throw new Error("no image base address found in the hex file.");
    }
    $("#imageVersion").text(hexify(image.version, 4));
    $("#imageBase").text(hexify(image.base, 4));
    $("#imageBinarySize").text(image.binary.length);
    $("#imageMd5").text(image.md5sum);
    $("#imageBinaryMd5").text(image.binarymd5sum);
    $('#basicInfo').show();
};

var handleFileSelect = function(evt) {
    var files = evt.target.files;
    var file = files[0];
    initImage();
    resetUi(false);

    var parseMeta = function(infoline) {
        // point of interests and corresponding properties should be updated of
        // the image
        var absoluteAddr;
        var idx;
        var versionAddr = 0x08000200;
        var binarySection = 0x08010000;

        switch (infoline.recordType) {
            case intelhex.DATA:
                absoluteAddr = infoline.address | image.currentBase;
                if ( versionAddr === absoluteAddr ){
                    image.version = readLeInt(infoline.data.slice(0, 4));
                    console.log('got version 0x' + image.version.toString(16));
                }
                else if ( image.currentBase === binarySection ) {
                    for (idx = 0; idx < infoline.data.length; ++idx) {
                        image.binary += String.fromCharCode(infoline.data[idx]);
                    }
                }
            break;
            case intelhex.EXT_LINEAR_ADDR:
                image.currentBase = infoline.data[1] | (infoline.data[0] << 8);
                image.currentBase <<= 16;
                console.log('got a linar addr, move base to 0x' + image.currentBase.toString(16));
            break;
            case intelhex.END_OF_FILE:
                image.base = image.currentBase;
                image.binarybase64value = window.btoa(image.binary);
                // FIXME should be md5 of binary file, but current md5 lib
                // cannot calculate it correctly
                image.binarymd5sum = hex_md5(image.binarybase64value);
                console.log('hex file over, base: 0x' + image.base.toString(16));
            break;
        }
    };

    if (files && file) {
        var reader = new window.FileReader();

        reader.onload = function(readerEvt) {
            var binaryString = readerEvt.target.result;
            try {
                intelhex.parse(binaryString, parseMeta);
                image.base64value = window.btoa(binaryString);
                image.md5sum = hex_md5(binaryString);
                fillInfo(image);
                $('#buttons').show();
            } catch (err) {
                setError(err);
                $('#buttons').hide();
            }
        };
        reader.readAsBinaryString(file);
    }
};


var setProgress = function(percentage) {
    var bar = $('#progressBar'),
        text = percentage.toString() + '%',
        span = $('#progressBar>span');

    bar.show().parent().show();
    if (percentage >= 0) {
        bar.removeClass('progress-bar-danger');
        bar.css('width', text);
        span.text(text);
        if (percentage === 100) {
            bar.addClass('progress-bar-success')
               .removeClass('progress-bar-striped');
        } else {
            bar.removeClass('progress-bar-success')
               .addClass('progress-bar-striped');
        }
    } else {
        bar.removeClass('progress-bar-success');
        bar.addClass('progress-bar-danger');
    }
};

var upload = function() {
    if (!image.base64value) {
        return;
    }
    var req = $.ajax({
        async: true,
        cache: false,
        dataType: 'json',
        method: 'POST',
        url: '/admin/image/upload',
        data: JSON.stringify(image),
        contentType: 'application/json',
        xhr: function () {
            var xhr = new window.XMLHttpRequest();
            //Download progress
            xhr.upload.onprogress = function (evt) {
                if (evt.lengthComputable) {
                    var percentComplete = evt.loaded / evt.total;
                    setProgress(Math.round(percentComplete * 100));
                } 
            };
            return xhr;
        },
        beforeSend: function () {
            setProgress(0);
            $('#btnUpload').disable();
            $('#btnReset').hide();
            $('#btnCancel').show().on('click', function() {
                req.abort();
            });
        },
        complete: function () {
            $('#btnReset').enable().show();
            $('#btnUpload').enable().show();
            $('#btnCancel').hide();
        },
        success: function (data) {
            console.log(data);
            $("#successMessage").text("Image uploaded successfully.");
            $('#infoBox').show();
        },
        error: function (xhr, status, error) {
            var errmsg = status;
            if (status === 'abort') {
                return;
            }
            if (xhr.status === 403) {
                window.location.href = '/admin/uploadimageview/';
                return;
            }
            if (xhr && xhr.responseText) {
                errmsg += ': ' + xhr.responseText;
            }
            else if (error && error.toString) {
                errmsg += ': ' + error.toString();
            }
            console.log(xhr);
            setError(errmsg);
            setProgress(-1);
        }
    });
    console.log('uploading...');
};

if (window.File && window.FileReader && window.FileList && window.Blob) {
    document.getElementById('filePicker').addEventListener('change', handleFileSelect, false);
    reset();
} else {
    window.alert('The File APIs are not fully supported in this browser.');
}

