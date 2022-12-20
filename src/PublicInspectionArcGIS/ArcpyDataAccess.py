# -*- coding: utf-8 -*-
import os
import arcpy

from arcpy import da
from PublicInspectionArcGIS.Utils import ToolboxLogger
from PublicInspectionArcGIS.DataAccess import DataAccess

class ArcpyDataAccess(DataAccess) :
    def __init__(self, workspace_path) :
        DataAccess.__init__(self)
        self.workspace_path = workspace_path
        self.__catalog_list = []
        self.__populate_catalog_list(self.workspace_path)
    
    def __populate_catalog_list(self, workspace) :
        for d in arcpy.Describe(workspace).children :
            if d.datatype == "FeatureDataset" :
                catalog_sub_list = self.__populate_catalog_list(d.catalogPath)
                self.__catalog_list += catalog_sub_list
            else :
                catalog_item = {}
                catalog_item["name"] = d.name 
                catalog_item["path"] = d.catalogPath
                self.__catalog_list.append(catalog_item)
        return self.__catalog_list

    def findTablePath(self, name) :
        items = [x for x in self.__catalog_list if x["name"] == name]
        item = items[0] if items else None
        return item["path"]

    def _getValue(self, cursor, row, fieldName):
        fields = tuple(f.lower() for f in cursor.fields)
        index = fields.index(fieldName.lower())
        if index > -1:
            return row[index]

    def _setValue(self, cursor, row, fieldName, value):
        fields = tuple(f.lower() for f in cursor.fields)
        index = fields.index(fieldName.lower())
        if index > -1:
            row[index] = value

    def query(self, table, fields="*", filter=None, geometry=False) :
        table_path = self.findTablePath(table)
        if(fields == "*" and geometry) :
            fields = ["*", "SHAPE@"]
        try:
            if filter == None:
                origin_cursor = da.SearchCursor(table_path, fields)
            else:
                origin_cursor = da.SearchCursor(table_path, fields, filter)

            output_registers = []
            fields = tuple(f for f in origin_cursor.fields)

            for origin_register in origin_cursor:
                output_register = {}
                for f in origin_cursor.fields:
                    index = fields.index(f)
                    output_register[f] = origin_register[index]
                output_registers.append(output_register)
            
            del origin_cursor

            return output_registers
        except Exception as e:
            ToolboxLogger.debug("ERROR: ---->{}".format(e))

    def add(self, table, fields, values) :
        table_path = self.findTablePath(table)
        table_fields = arcpy.ListFields(table_path)
        oid_field = [f.name for f in table_fields if f.type == "OID"][0]
        domain_fields = [f for f in table_fields if f.domain != '']
        for domain_field in domain_fields:
            if not fields.__contains__(domain_field.name) and domain_field.defaultValue != '':
                fields.append(domain_field.name)
                for value in values:
                    index = values.index(value)
                    value_list = list(value)
                    value_list.append(domain_field.defaultValue)
                    values[index] = tuple(value_list)

        edit = da.Editor(self.workspace_path)
        edit.startEditing(with_undo=False, multiuser_mode=False)
        edit.startOperation()

        cursor = da.InsertCursor(table_path, fields)

        inserted_id = []
        for row in values:
            id = cursor.insertRow(row)
            inserted_id.append(id) 

        del row
        del cursor

        edit.stopOperation()
        edit.stopEditing(save_changes=True)        

        register = self.query(table, "*", "{} = {}".format(oid_field, inserted_id[0]))
        return register

    def update(self, table, fields, values, filter = None) :
        table_path = self.findTablePath(table)

        edit = da.Editor(self.workspace_path)
        edit.startEditing(with_undo=False, multiuser_mode=False)
        edit.startOperation()

        if filter:
            cursor = da.UpdateCursor(table_path, fields, filter)
        else :
            cursor = da.UpdateCursor(table_path, fields)
        
        for row in cursor:
            for field in fields:
                index = fields.index(field)
                row[index] =values[index]
            cursor.updateRow(row)

        del row
        del cursor

        edit.stopOperation()
        edit.stopEditing(save_changes=True)

    def delete(self, table, fields = None, filter = None):
        table_path = self.findTablePath(table)
        if fields == None :
            fields = "*"

        edit = da.Editor(self.workspace_path)
        edit.startEditing(with_undo=False, multiuser_mode=False)
        edit.startOperation()

        if filter:
            cursor = da.UpdateCursor(table_path, fields, filter)
        else :
            cursor = da.UpdateCursor(table_path, fields)
        
        for row in cursor:
            cursor.deleteRow()

        del cursor

        edit.stopOperation()
        edit.stopEditing(save_changes=True)
