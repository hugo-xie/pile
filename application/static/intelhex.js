/*jslint browser: true*/

var intelhex = {
};

intelhex.DATA = 0;
intelhex.END_OF_FILE = 1;
intelhex.EXT_SEGMENT_ADDR = 2;
intelhex.START_SEGMENT_ADDR = 3;
intelhex.EXT_LINEAR_ADDR = 4;
intelhex.START_LINEAR_ADDR = 5;

intelhex.parse = function parseIntelHexData(hex, callback) {
    console.log('loaded file');
    // Split the file into lines
    var hexLines = hex.split('\n');
    var i, j, b, checksum, expectedCsum,
        line, byteCount, address,
        recordType, startIndex, dataIndex;
    var buf;

    if (hexLines[hexLines.length - 1].length === 0) {
        // The last line is an empty string
        hexLines.pop();
    }

    // For each line
    for (i = 0; i < hexLines.length; i++) {
        // Grab the line
        line = hexLines[i].trim();

        if(line.charAt(0) !== ":") {
            throw new Error("Line " + (i+1) +
                            ": '" + line + "'" +
                            " does not start with a colon (:).");
        }
        // Save the byte count
        byteCount = parseInt(line.substr(1, 2), 16);
        // Save the address
        address = parseInt(line.substr(3, 4), 16);
        // Save the record type
        recordType = parseInt(line.substr(7, 2), 16);
        // First data byte is at byte 9
        startIndex = 9;
        // Save the checksum
        expectedCsum = parseInt(line.substr(startIndex + 2 * byteCount, 2), 16);

        if(line.length !== startIndex + 2 * byteCount + 2) {
            throw new Error(
                "Line " + (i+1) +
                ": '" + line + "'" +
                " has more chars then expected (" + 
                (startIndex + 2 * byteCount + 2) + ")"
            );
        }

        checksum = byteCount + (address & 0xff) + ((address & 0xff00) >> 8) + recordType;

        buf = [];

        // For each byte
        for (j = 0; j < byteCount; j++) {
            // Get the index of the next byte
            dataIndex = startIndex + (j * 2);
            // Interpret two characters as a hex digit
            b = parseInt(line.substr(dataIndex, 2), 16);
            checksum += b;
            buf.push(b);
        }

        checksum = 0x100 - (0xff & checksum);
        checksum &= 0xff;

        if(checksum !== expectedCsum) {
            throw new Error(
                "Line " + (i+1) +
                ": '" + line + "'" +
                " checksum check failed, expected " + expectedCsum + " but got " + checksum + "."
            );
        }
        if (callback && false === callback({
            'byteCount': byteCount,
            'recordType': recordType, 
            'address': address, 
            'checksum': expectedCsum,
            'data': buf
            })
        ) {
            break;
        }
    }

    console.log("Finished!");

};
