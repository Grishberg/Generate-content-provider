__author__ = 'g'


class Generator:
    def __init__(self, rootPackage, dbName):
        self.pkg = rootPackage
        self.dbName = dbName

    def getClassName(self, s):
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
                fieldConstName =  self.generateConstName(fieldName)
                fieldParam = ""
                if len(words) > 2:
                    for i in range(2, len(words)):
                        fieldParam += words[i]+' '
                fields.append({'name': fieldName, 'type': fieldType, 'param': fieldParam, 'const': fieldConstName})
        if tableName is not None:
            tables.append({"name": tableName, "fields": fields})
        self.generateHelper(tables)

    def generateHelper(self, tables):
        out = ""
        out += "package " + self.pkg + ";\n\n"
        out += "import android.content.ContentValues;\n"
        out += "import android.content.Context;\n"
        out += "import android.database.sqlite.SQLiteDatabase;\n"
        out += "import android.database.sqlite.SQLiteOpenHelper;\n"
        out += "public class DbHelper extends SQLiteOpenHelper {\n"
        out += '\tprivate static final String DB_NAME = "' + self.dbName + '";\n'
        out += "\tprivate static final int DB_VERSION = 1;\n"
        out += '\tpublic static final String COLUMN_ID = "_id";\n'
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
            out += '\t\t"CREATE TABLE "+'+constTableName + ' "("+\n'

            for i in range(0, len(fields)):
                field = fields[i]
                out += '\t\t' + field['const'] + ' + " ' + field['param']
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
            out += "\t\t\t"+ "CRATE_TABLE_"+constTableName
            if i < len(tables) - 1 :
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
        f = open("DbHelper.java", "w")
        f.write(out)
        f.close()


pkg = "com.test.data.db"
dbName = "test.db"
g = Generator(pkg, dbName)

f = open("in.txt", "r")
buf = f.read()
f.close()

g.parseTemp(buf)
