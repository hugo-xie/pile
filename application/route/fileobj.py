from .. import api, app, db
from flask import Response
from flask_restful import Resource, request, abort
from .keys import Key
from ..const import UPLOAD_SIZE, ErrNo, result
from ..model.fileobj import FileObj


class AddFile(Resource):
    """
    This class saves uploaded file into database.
    Errors:
        PARAM: invalid parameters for user input
        DB: database operation failure
    """
    def __init__(self):
        super(AddFile, self).__init__()

    def post(self):
        file = request.files[Key.file.name]
        if not file:
            return result(ErrNo.PARAM)

        try:
            obj = file.read()
            if len(obj) > UPLOAD_SIZE:
                return result(ErrNo.BIG)
            fobj = FileObj(mime_type=file.mimetype, obj=obj)
            db.session.add(fobj)
            db.session.commit()
        except Exception as e:
            return result(ErrNo.DB, msg=str(e))
        return result(ErrNo.OK, id=fobj.id)


@app.route('/v1/file/get/<id>')
def get_file(id):
    """
    This function fetches file object from database according to id.
    :param id: file object id
    :return: response object including file data
    """
    try:
        fobj = db.session.query(FileObj).get(id)
        if fobj is None:
            abort(404)
        return Response(fobj.obj, mimetype=fobj.mime_type)
    except Exception as e:
        abort(404, message=str(e))

api.add_resource(AddFile, '/v1/file/add')



