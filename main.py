import os

__author__ = 'g'


class Generator:
    def __init__(self, rootPackage, dbName):
        self.pkg = rootPackage
        self.dbName = dbName
        self.cwd = os.path.dirname(os.path.abspath(__file__))+"/out/"
        self.modelsPath = self.cwd+"model/"
        if not os.path.exists(self.modelsPath): os.makedirs(self.modelsPath)

    def generateSqlType(self, s):
        s = s.lower()
        if s == "string":
            return "TEXT"
        elif s == "int":
            return "INTEGER"
        elif s == "long":
            return "INTEGER"
        elif s == "date":
            return "INTEGER"
        elif s == "boolean":
            return "INTEGER"

    def generateCursorGetter(self, s):
        s = s.lower()
        if s == "string":
            return "getString"
        elif s == "int":
            return "getInt"
        elif s == "long":
            return "getLong"
        elif s == "date":
            return "getLong"
        elif s == "boolean":
            return "getInt"

    def generateClassName(self, s):
        out = s[0].upper() + s[1:]
        arr = out.split("_")
        if len(arr) > 0:
            out = ""
            for i in arr:
                out += i[0].upper() + i[1:]
        return out

    def generateVarName(self, oldName):
        newName = ""
        lst = oldName.lower().split("_")
        firstSymbol = 1
        for i in lst:
            if firstSymbol:
                newName += i[0].lower()
                firstSymbol = 0
            else:
                newName += i[0].upper()
            if len(i) > 1:
                newName += i[1:]
        return newName

    def generateConstName(self, name):
        out = []
        upper = 0
        for i in name:
            if i.upper() == i:
                if upper == 0:
                    # camel
                    out.append("_")
                    out.append(i)
                else:
                    out.append(i)
                upper = 1
            else:
                if upper == 1:
                    if out[-2] != '_':
                        out.insert(-1, '_')
                upper = 0
                out.append(i)
        sOut = ""
        for i in out:
            sOut += i
        if sOut.find("__") > 0:
            sOut = sOut.replace("__", "_")
        return sOut.upper()

    # парсинг шаблона с таблицами и полями бд
    def parseTemp(self, inBuffer):
        lst = inBuffer.split("\n")
        tables = []
        tableName = None
        fields = []
        for row in lst:
            line = row.strip()
            words = line.split(" ")
            if len(line) > 0 and len(words) == 1:
                # table name
                if tableName is not None:
                    tables.append({"name": tableName, "fields": fields})
                fields = []
                tableName = line
            elif len(words) > 1:
                # fields
                fieldName = words[0]
                fieldType = words[1]
                fieldSqlType = self.generateSqlType(fieldType)
                varName = self.generateVarName(words[0])
                fieldConstName =  self.generateConstName(fieldName)
                fieldParam = ""
                if len(words) > 2:
                    for i in range(2, len(words)):
                        fieldParam += words[i]+' '
                fields.append({'name': fieldName, 'type': fieldType, 'sqlType': fieldSqlType, 'param': fieldParam, 'const': fieldConstName, 'varName':varName})
        if tableName is not None:
            tables.append({"name": tableName, "fields": fields})
        self.generateHelper(tables)
        self.generateContentProvider(tables)
        self.generateModels(tables)
        self.generateApp(tables)

    # формирование SqlHelper
    def generateHelper(self, tables):
        out = ""
        out += "package " + self.pkg + ".data.db;\n\n"
        out += "import android.content.ContentValues;\n"
        out += "import android.content.Context;\n"
        out += "import android.database.sqlite.SQLiteDatabase;\n"
        out += "import android.database.sqlite.SQLiteOpenHelper;\n"
        out += "public class DbHelper extends SQLiteOpenHelper {\n"
        out += '\tprivate static final String DB_NAME = "' + self.dbName + '";\n'
        out += "\tprivate static final int DB_VERSION = 1;\n"
        out += '\tpublic static final String COLUMN_ID = "_id";\n'
        #tables and fields
        for t in tables:
            out += "\t// " + t["name"] + "\n"
            constTableName = self.generateConstName(t["name"])
            out += "\tpublic static final String TABLE_" + constTableName + ' = "' + t["name"] + '";\n'

            for v in t["fields"]:
                name = v["name"]
                nameConst = self.generateConstName(name)
                out += "\tpublic static final String " + constTableName + "_" + nameConst + ' = "' + name + '";\n'

        out += "\n"
        for t in tables:
            fields = t["fields"]
            tableName = t["name"]
            out += "\t// " + tableName + "\n"
            constTableName = self.generateConstName(tableName)
            out += "\tprivate static final String CREATE_TABLE_"+ constTableName + ' ="" +\n'
            out += '\t\t"CREATE TABLE "+TABLE_'+constTableName + ' + "("+\n'
            out += '\t\tCOLUMN_ID + " integer primary key," +\n'
            for i in range(0, len(fields)):
                field = fields[i]
                out += '\t\t' + constTableName +"_"+ field['const'] + ' + " ' + field['sqlType'] + " " + field['param']
                if i < len(fields) - 1:
                    out += ","
                out += '" +\n'

            out += '\t\t");";\n'

        out += "\tpublic DbHelper(Context context) {\n"
        out += "\t\tsuper(context, DB_NAME, null, DB_VERSION);\n"
        out += "\t}\n"

        out += "\t@Override\n"
        out += "\tpublic void onCreate(SQLiteDatabase db) {\n"
        out += "\t\tString[] CREATES = {\n"
        for i in range(len(tables)):
            constTableName =  self.generateConstName( tables[i]["name"] )
            out += "\t\t\t"+ "CREATE_TABLE_"+constTableName
            if i < len(tables) - 1:
                out += ","
            out += "\n"
        out += "\t\t};\n"

        out += "\t\tfor (final String table : CREATES) {\n"
        out += "\t\t\t" + "db.execSQL(table);\n"
        out += "\t\t}\n"
        out += "\t};\n"

        out += "\t@Override\n"
        out += "\tpublic void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {\t\n"
        out += "\t\tString[] TABLES = {\n"

        for i in range(len(tables)):
            constTableName = self.generateConstName( tables[i]["name"] )
            out += "\t\t\t"+ "TABLE_"+constTableName
            if i < len(tables) - 1 :
                out += ","
            out += "\n"

        out += "\t\t};\n"

        out += "\t\tfor (final String table : TABLES) {\n"
        out += '\t\t\tdb.execSQL("DROP TABLE IF EXISTS " + table);\n'
        out += '\t\t}\n'

        out += '\t\tonCreate(db);\n'
        out += "\t}\n"
        out += "}\n"
        f = open(self.cwd+"DbHelper.java", "w")
        f.write(out)
        f.close()

    # формирование контент провайдера
    def generateContentProviderImport(self, tables):
        out = "package "+ self.pkg + ".data.db;\n"
        out += "import "+ self.pkg + ".data.db.DbHelper;\n"
        out += "import android.content.ContentProvider;\n"
        out += "import android.content.ContentUris;\n"
        out += "import android.content.ContentValues;\n"
        out += "import android.content.Context;\n"
        out += "import android.content.UriMatcher;\n"
        out += "import android.database.Cursor;\n"
        out += "import android.database.sqlite.SQLiteConstraintException;\n"
        out += "import android.database.sqlite.SQLiteDatabase;\n"
        out += "import android.net.Uri;\n"
        out += "import android.text.TextUtils;\n\n"
        out += "//generated by CP-generator\n"
        out += "public class AppContentProvider extends ContentProvider {\n"
        out += '\tprivate static final String AUTHORITY = "' + self.pkg + '.content_provider";\n'
        #path
        for t in tables:
            tableName = t["name"]
            constTableName = self.generateConstName(tableName)
            out += '\tprivate static final String PATH_'+constTableName+ ' = DbHelper.TABLE_'+constTableName + ';\n'
        out += '\n'
        #url
        for t in tables:
            tableName = t["name"]
            constTableName = self.generateConstName(tableName)
            out += '\tpublic static final Uri CONTENT_URI_'+constTableName+ \
                   ' = Uri.parse("content://" + AUTHORITY +"/" +PATH_' + constTableName + ');\n'
        out += '\n'
        #code
        index = 0
        for t in tables:
            tableName = t["name"]
            constTableName = self.generateConstName(tableName)
            out += '\tprivate static final int CODE_'+constTableName+ ' = '+str(index) + ';\n'
            index += 1
        out+="\tprivate static final UriMatcher URI_MATCHER = new UriMatcher(UriMatcher.NO_MATCH);\n\n"

        out += "\tstatic {\n"

        for t in tables:
            tableName = t["name"]
            constTableName = self.generateConstName(tableName)
            out += '\t\tURI_MATCHER.addURI(AUTHORITY, PATH_'+constTableName+ ', CODE_'+ constTableName+ ');\n'
        out +="\t}\n"

        out+="\tprivate static DbHelper dbHelper;\n\n"
        out+='\tpublic synchronized static DbHelper getDbHelper(Context context) {\n'
        out+='\t\tif (null == dbHelper) {\n'
        out+='\t\t\tdbHelper = new DbHelper(context);\n'
        out += '\t\t}\n'
        out += '\t\treturn dbHelper;\n'
        out += '\t}\n\n'

        out +='\n'
        out +='\t@Override\n'
        out +='\tpublic boolean onCreate() {\n'
        out +='\t\tgetDbHelper(getContext());\n'
        out +='\t\treturn true;\n'
        out +='\t}\n'

        # parseUri
        out +='\tprivate String parseUri(Uri uri) {\n'
        out +='\t\treturn parseUri(URI_MATCHER.match(uri));\n'
        out +='\t}\n\n'

        # parseUri
        out +='\tprivate String parseUri(int match) {\n'
        out +='\t\tString table = null;\n'
        out +='\t\tswitch (match) {\n'
        for t in tables:
            tableName = t["name"]
            constTableName = self.generateConstName(tableName)
            out += '\t\t\tcase CODE_'+constTableName+ ':\n'
            out += '\t\t\t\ttable = dbHelper.TABLE_' + constTableName+ ';\n'
            out += '\t\t\t\tbreak;\n'

        out += '\t\t\tdefault:\n'
        out += '\t\t\t\tthrow new IllegalArgumentException("Invalid DB code: " + match);\n'
        out += "\t\t}\n"
        out += "\t\treturn table;\n"
        out += '\t}\n'
        out += '\t@Override\n'
        out += '\tpublic String getType(Uri uri) {\n'
        out += '\t\treturn null;\n'
        out += '\t}\n\n'

        return out

    def generateQuery(self, tables):
        out = ""
        out += "\t@Override\n"
        out += "\tpublic Cursor query(Uri uri, String[] projection, String selection\n" \
               "\t\t\t, String[] selectionArgs, String sortOrder) {\n"
        out += "\t\tint uriId = URI_MATCHER.match(uri);\n"
        out += "\t\tCursor cursor = null;\n"
        out += '\t\tswitch(uriId){\n'
        for t in tables:
            tableName = t["name"]
            constTableName = self.generateConstName(tableName)
            out += '\t\t\tcase CODE_' + constTableName + ':\n'
            out += '\t\t\t\tcursor = dbHelper.getReadableDatabase()\n'
            out += '\t\t\t\t\t.query(DbHelper.TABLE_' + constTableName+ ', projection, selection\n'
            out += '\t\t\t\t\t,selectionArgs, null, null, sortOrder);\n'
            out += '\t\t\t\tbreak;\n'

        out += '\t\t\tdefault:\n'
        out += '\t\t\t\tthrow new IllegalArgumentException("Invalid DB code: " + uri);\n'
        out += "\t\t}\n"

        out += "\t\tcursor.setNotificationUri(getContext().getContentResolver(), uri);\n"
        out += "\t\treturn cursor;\n"
        out += "\t}\n\n"
        return out

    def generateInsert(self, tables):
        out = ""
        out += "\t@Override\n"
        out += "\tpublic Uri insert(Uri uri, ContentValues values) {\n"
        out += "\t\tlong id = -1;\n"
        out += "\t\tint uriId = URI_MATCHER.match(uri);\n"
        out += "\t\tString table = parseUri(uri);\n"
        out += "\t\tSQLiteDatabase db = dbHelper.getWritableDatabase();\n"
        out += '\t\tswitch(uriId){\n'
        for t in tables:
            tableName = t["name"]
            constTableName = self.generateConstName(tableName)
            out += '\t\t\tcase CODE_' + constTableName + ':\n'
            out += '\t\t\t\tid = db.insert(table, null, values);\n'
            out += '\t\t\t\t\t.query(DbHelper.TABLE_' + constTableName+ ', projection, selection\n'
            out += '\t\t\t\t\t,selectionArgs, null, null, sortOrder);\n'
            out += '\t\t\t\tbreak;\n'
        out += '\t\t\tdefault:\n'
        out += '\t\t\t\tid = insertOrUpdateById(db,uri,table,values,DbHelper.COLUMN_ID);\n'
        out += "\t\t}\n"
        out += "\t\tUri resultUri = ContentUris.withAppendedId(uri, id);\n"
        out += "\t\tgetContext().getContentResolver().notifyChange(resultUri, null);\n"
        out += "\t\treturn resultUri;\n"
        out += "\t}\n\n"
        return out

    def generateUpdate(self, tables):
        out = ""
        out += "\t@Override\n"
        out += "\tpublic int update(Uri uri, ContentValues values, String selection, String[] selectionArgs) {\n"
        out += "\t\tint result = 0;\n"
        out += "\t\t//int uriId = URI_MATCHER.match(uri);\n"
        out += "\t\tString table = parseUri(uri);\n"
        out += "\t\tSQLiteDatabase db = dbHelper.getWritableDatabase();\n"
        out += "\t\tresult	= db.update(table, values, selection, selectionArgs);\n"
        out += "\t\tgetContext().getContentResolver().notifyChange(uri, null);\n"
        out += "\t\treturn result;\n"
        out += "\t}\n\n"
        return out

    def generateDelete(self, tables):
        out = ""
        out += "\t@Override\n"
        out += "\tpublic int delete(Uri uri, String selection, String[] selectionArgs) {\n"
        out += "\t\tint result = 0;\n"
        out += "\t\t//int uriId = URI_MATCHER.match(uri);\n"
        out += "\t\tString table = parseUri(uri);\n"
        out += "\t\tSQLiteDatabase db = dbHelper.getWritableDatabase();\n"
        out += "\t\tresult = db.delete(table, selection, selectionArgs);\n"
        out += "\t\tgetContext().getContentResolver().notifyChange(uri, null);\n"
        out += "\t\treturn result;\n"
        out += "\t}\n\n"
        return out


    def generateInserOrUpdate(self):
        out = ""
        out += "\tprivate long insertOrUpdateById(SQLiteDatabase db, Uri uri, String table,\n"
        out += "\t\tContentValues values, String column) throws SQLiteConstraintException{\n"
        out += "\t\tlong result	= -1;\n"
        out += "\t\ttry {\n"
        out += "\t\t\tresult = db.insertOrThrow(table, null, values);\n"
        out += "\t\t} catch (SQLiteConstraintException e) {\n"
        out += '\t\t\tint nrRows = update(uri, values, column + "=?",\n'
        out += '\t\t\t\tnew String[]{values.getAsString(column)});\n'
        out += "\t\t\tif (nrRows == 0) {\n"
        out += "\t\t\t\tthrow e;\n"
        out += "\t\t\t}\n"
        out += "\t\t}\n"
        out += "\t\treturn result;\n"
        out += "\t}\n\n"
        return out

    def generateContentProvider(self, tables):
        out = ""
        out += self.generateContentProviderImport(tables)
        out += self.generateQuery(tables)
        out += self.generateInsert(tables)
        out += self.generateUpdate(tables)
        out += self.generateDelete(tables)
        out += self.generateInserOrUpdate()
        out += "}\n"

        f = open(self.cwd+"AppContentProvider.java", "w")
        f.write(out)
        f.close()

    def generateModels(self, tables):
        for t in tables:
            fields = t['fields']
            tableName = t['name']
            constTableName = self.generateConstName(tableName)
            className = self.generateClassName(tableName)
            out = "package " + self.pkg + ".data.db.model;\n"
            out += "import " + self.pkg + ".data.db.DbHelper;\n"

            out += "import android.content.ContentValues;\n"
            out += "import android.database.Cursor;\n\n"
            out += "public class "+className + "{\n"
            out += '\tprivate long id;\n'
            for v in t["fields"]:
                varName = v['varName']
                out += "\tprivate "+v['type'] + " " + varName + ";\n"

            out += "\n"
            out += "\tpublic "+className + "(long id\n"
            for i in range(0, len(fields)):
                field = fields[i]
                varName = field['varName']
                out += "\t\t\t," + field['type'] + ' ' + varName
                if i < len(fields)-1:
                    out += "\n"
            out += " ){\n"

            out += '\t\tthis.id = id;\n'
            for v in t["fields"]:
                varName = v['varName']
                out += "\t\tthis." + varName + " = " + varName + ";\n"

            out += "\t}\n"

            out += "\tpublic static " + className + " fromCursor(Cursor c){\n"
            out += "\t\tint idColId = c.getColumnIndex(DbHelper.COLUMN_ID);\n"
            for v in t["fields"]:
                varName = v['varName']
                out += "\t\tint " + varName + "Id = c.getColumnIndex(DbHelper." + constTableName + "_" + v['const']+");\n"

            out += "\t\treturn new " + className + "( \n"
            out += '\t\t\tc.getLong(idColId)\n'
            for i in range(0, len(fields)):
                v = fields[i]
                varName = v['varName']
                out += "\t\t\t, c." + self.generateCursorGetter(v['type']) + "(" +varName + "Id)"
                if i < len(fields)-1:
                    out += "\n"
            out += " );\n"
            out += "\t}\n"

            out += "\tpublic ContentValues buildContentValues(){\n"
            out += "\t\tContentValues cv = new ContentValues();\n"
            out += "\t\tif (id >= 0) {\n"
            out += "\t\t\tcv.put(DbHelper.COLUMN_ID, id);\n\t\t}\n"

            for v in t["fields"]:
                varName = v['varName']
                constVarName = self.generateConstName(varName)
                constTableName = self.generateConstName(tableName)
                out += "\t\tcv.put(DbHelper." +constTableName + "_" +  constVarName + ", " + varName +");\n"
            out += "\t\treturn cv;\n"
            out += "\n"
            out += "\t}\n"
            out += "\n\t------------- getters ------------\n"
            # generateGetters
            for v in t["fields"]:
                varName = v['varName']
                out += "\tpublic " + v['type'] +" get" + self.generateClassName(varName) + "(){\n"
                out += "\t\treturn " + varName + ";\n"
                out += "\t}\n\n"

            out += "}\n"
            f = open(self.modelsPath+className+".java", "w")
            f.write(out)
            f.close()

    #generate App class
    def generateApp(self, tables):
        out = ""
        out = "package " + self.pkg + ";\n\n"
        out += "import " + self.pkg + ".data.db.DbHelper;\n\n"
        out += "import android.app.Application;\n"
        out += "import android.content.Context;\n"
        out += "import " + self.pkg + ".data.db.AppContentProvider;\n\n"

        for t in tables:
            tableName = t['name']
            className = self.generateClassName(tableName)
            out += "import "+ self.pkg + ".data.db.model." + className + ";\n"

        out += "\nprivate static App mInstance;\n"
        out += "private static Context mAppContext;\n\n"
        out += "public class App extends Application {\n"
        out += "\t@Override\n"
        out += "\tpublic void onCreate() {\n"
        out += "\t\tsuper.onCreate();\n"
        out += "\t\tmInstance = this;\n"
        out += "\t\tmAppContext = getApplicationContext();\n"
        out += "\t}\n\n"

        out += "\tpublic static App getInstance() {\n"
        out += "\t\treturn mInstance;\n"
        out += "\t}\n\n"

        out += "\tpublic static Context getAppContext() {\n"
        out += "\t\treturn mAppContext;\n"
        out += "\t}\n\n"

        for t in tables:
            fields = t['fields']
            tableName = t['name']
            constTableName = self.generateConstName(tableName)
            className = self.generateClassName(tableName)
            out += "\tpublic static void insert" + className + "( " + className + " value ){\n"
            out += "\t\tmAppContext.getContentResolver()\n"
            out += "\t\t\t.insert(AppContentProvider.CONTENT_URI_"+constTableName + "\n"
            out += "\t\t\t\t, value.buildContentValues());\n"
            out += "\t}\n"

        out += "}\n"

        f = open(self.cwd+"App.java", "w")
        f.write(out)
        f.close()


pkg = "com.grishberg.oauth2test"
dbName = "cache.db"
g = Generator(pkg, dbName)

f = open("in.txt", "r")
buf = f.read()
f.close()

g.parseTemp(buf)
