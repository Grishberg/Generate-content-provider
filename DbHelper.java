package com.test.data.db;

import android.content.ContentValues;
import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
public class DbHelper extends SQLiteOpenHelper {
	private static final String DB_NAME = "test.db";
	private static final int DB_VERSION = 1;
	public static final String COLUMN_ID = "_id";
	// tableName1
	public static final String TABLE_TABLE_NAME_1 = "tableName1";
	public static final String TABLE_NAME_1_FIELD_1 = "field1";
	public static final String TABLE_NAME_1_FIELD_2 = "field2";
	// tableName2
	public static final String TABLE_TABLE_NAME_2 = "tableName2";
	public static final String TABLE_NAME_2_FIELD_1 = "field1";
	public static final String TABLE_NAME_2_FIELD_2 = "field2";

	// tableName1
	private static final String CREATE_TABLE_TABLE_NAME_1 ="" +
		"CREATE TABLE "+TABLE_NAME_1 "("+
		FIELD_1 + " primary key autoincrement ," +
		FIELD_2 + " " +
		");";
	// tableName2
	private static final String CREATE_TABLE_TABLE_NAME_2 ="" +
		"CREATE TABLE "+TABLE_NAME_2 "("+
		FIELD_1 + " ," +
		FIELD_2 + " " +
		");";
	public DbHelper(Context context) {
		super(context, DB_NAME, null, DB_VERSION);
	}
	@Override
	public void onCreate(SQLiteDatabase db) {
		String[] CREATES = {
			CRATE_TABLE_TABLE_NAME_1,
			CRATE_TABLE_TABLE_NAME_2
		};
		for (final String table : CREATES) {
			db.execSQL(table);
		}
	};
	@Override
	public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {	
		String[] TABLES = {
			TABLE_TABLE_NAME_1,
			TABLE_TABLE_NAME_2
		};
		for (final String table : TABLES) {
			db.execSQL("DROP TABLE IF EXISTS " + table);
		}
		onCreate(db);
	}
}
