import sys
from Jumpscale import j
from collections import OrderedDict

# import capnp


class Tools(j.baseclasses.object):
    def listInDictCreation(self, listInDict, name, manipulateDef=None):
        """
        check name exist in the dict
        then check its a dict, if yes walk over it and make sure they become strings or use the manipulateDef function
        string 'a,b,c' gets translated to list
        @param manipulateDef if None then will make it a string, could be e.g. int if you want to have all elements to be converted to int
        """
        if name in listInDict:
            if j.data.types.list.check(listInDict[name]):
                if manipulateDef is None:
                    listInDict[name] = [str(item).strip() for item in listInDict[name]]
                else:
                    listInDict[name] = [manipulateDef(item) for item in listInDict[name]]
            else:
                if manipulateDef is None:
                    if "," in str(listInDict[name]):
                        listInDict[name] = [item.strip() for item in listInDict[name].split(",") if item.strip() != ""]
                    else:
                        listInDict[name] = [str(listInDict[name])]
                else:
                    listInDict[name] = [manipulateDef(listInDict[name])]
        return listInDict


class Capnp(j.baseclasses.object):
    """
    """

    __jslocation__ = "j.data.capnp"

    def _init(self, **kwargs):
        self._schema_cache = {}
        self._capnpVarDir = j.sal.fs.joinPaths(j.dirs.VARDIR, "capnp")
        j.sal.fs.createDir(self._capnpVarDir)
        if self._capnpVarDir not in sys.path:
            sys.path.append(self._capnpVarDir)
        self.tools = Tools()

    def getId(self, schemaInText):
        r = None
        for line in schemaInText.split("\n"):
            line = line.strip()
            if line.startswith("@0x"):
                if r:
                    raise j.exceptions.Input("can only have 1 capnp_id in file", data=schemaInText)
                r = line.strip()[3:-1]
        if not r:
            raise j.exceptions.Input("did not find capnp_id in file", data=schemaInText)
        return r

    def removeFromCache(self, schemaId):
        self._schema_cache.pop(schemaId, None)

    def resetSchema(self, schemaId):
        self._schema_cache.pop(schemaId, None)
        nameOnFS = "schema_%s.capnp" % (schemaId)
        path = j.sal.fs.joinPaths(self._capnpVarDir, nameOnFS)
        if j.sal.fs.exists(path):
            j.sal.fs.remove(path)

    def _getSchemas(self, schemaInText):
        import capnp

        schemaInText = j.core.text.strip(schemaInText)
        schemaInText = schemaInText.strip() + "\n"
        schemaId = self.getId(schemaInText)
        if schemaId not in self._schema_cache:
            nameOnFS = "schema_%s.capnp" % (schemaId)
            path = j.sal.fs.joinPaths(self._capnpVarDir, nameOnFS)
            j.sal.fs.writeFile(filename=path, contents=schemaInText, append=False)
            parser = capnp.SchemaParser()
            try:
                schema = parser.load(path)
            except Exception as e:
                msg = str(e)
                raise j.exceptions.Base("%s\n\nERROR:Could not parse capnp schema:\n%s" % (schemaInText, msg))
            self._schema_cache[schemaId] = schema
        return self._schema_cache[schemaId]

    def getSchemaFromText(self, schemaInText, name="Schema"):
        # if not schemaInText.strip():
        #     schemaInText = (
        #         """
        #     @%s;
        #     struct Schema {
        #
        #     }
        #     """
        #         % j.data.idgenerator.generateCapnpID()
        #     )

        schemas = self._getSchemas(schemaInText)
        schema = eval("schemas.%s" % name)
        return schema

    def getSchemaFromPath(self, path, name):
        """
        @param path is path to schema
        """
        content = j.sal.fs.readFile(path)
        return self.getSchemaFromText(schemaInText=content, name=name)

    def _ensure_dict(self, args):
        """
        make sure the argument schema are of the type dict
        capnp doesn't handle building a message with OrderedDict properly
        """
        if isinstance(args, OrderedDict):
            args = dict(args)
            for k, v in args.items():
                args[k] = self._ensure_dict(v)
        if isinstance(args, list):
            for i, v in enumerate(args):
                args.insert(i, self._ensure_dict(v))
                args.pop(i + 1)
        return args

    def getObj(self, schemaInText, name="Schema", args={}, binaryData=None):
        """
        @PARAM schemaInText is capnp schema
        @PARAM name is the name of the obj in the schema e.g. Issue
        @PARAM args are the starting date for the obj, normally a dict
        @PARAM binaryData is this is given then its the binary data to
               create the obj from, cannot be sed together with args
               (its one or the other)
        """

        # . are removed from . to Uppercase
        args = args.copy()  # to not change the args passed in argument
        for key in list(args.keys()):
            sanitize_key = j.core.text.sanitize_key(key)
            if key != sanitize_key:
                args[sanitize_key] = args[key]
                args.pop(key)

        schema = self.getSchemaFromText(schemaInText, name=name)

        if binaryData is not None and binaryData != b"":
            obj = schema.from_bytes_packed(binaryData).as_builder()
        else:
            try:
                args = self._ensure_dict(args)
                obj = schema.new_message(**args)
            except Exception as e:
                if str(e).find("has no such member") != -1:
                    msg = "cannot create data for schema from "
                    msg += "arguments, property missing\n"
                    msg += "arguments:\n%s\n" % j.data.serializers.json.dumps(args, sort_keys=True, indent=True)
                    msg += "schema:\n%s" % schemaInText
                    ee = str(e).split("stack:")[0]
                    ee = ee.split("failed:")[1]
                    msg += "capnperror:%s" % ee
                    self._log_debug(msg)
                    raise j.exceptions.Input(message=msg)
                if str(e).find("Value type mismatch") != -1:
                    msg = "cannot create data for schema from "
                    msg += "arguments, value type mismatch.\n"
                    msg += "arguments:\n%s\n" % j.data.serializers.json.dumps(args, sort_keys=True, indent=True)
                    msg += "schema:\n%s" % schemaInText
                    ee = str(e).split("stack:")[0]
                    ee = ee.split("failed:")[1]
                    msg += "capnperror:%s" % ee
                    self._log_debug(msg)
                    raise j.exceptions.Input(message=msg)
                raise e

        return obj

    def test(self):
        """
        kosmos 'j.data.capnp.test()'
        """
        import time

        capnpschema = """
        @0x9fc1ac9f09464fc9;

        struct Issue {

          state @0 :State;
          enum State {
            new @0;
            ok @1;
            error @2;
            disabled @3;
          }

          #name of actor e.g. node.ssh (role is the first part of it)
          name @1 :Text;
          descr @2 :Text;

        }
        """

        # dummy test, not used later
        obj = self.getObj(capnpschema, name="Issue")
        assert obj.state == "new"
        obj.state = "ok"

        # now we just get the capnp schema for this object
        schema = self.getSchemaFromText(capnpschema, name="Issue")
        obj = schema.new_message()
        assert obj.state == "new"

    def getJSON(self, obj):
        configdata2 = obj.to_dict()
        ddict2 = OrderedDict(configdata2)
        return j.data.serializers.json.dumps(ddict2, sort_keys=True, indent=True)

    def getBinaryData(self, obj):
        return obj.to_bytes_packed()
