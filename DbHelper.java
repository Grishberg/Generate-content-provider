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
