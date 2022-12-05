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

    def _search_da(self, origin_table, fields, filter=None, geometry=False) :
        origin_table = os.path.join(self.workspace_path, origin_table)
        if(fields == "*" and geometry) :
            fields = ["*", "SHAPE@"]
        try:
            if filter == None:
                origin_cursor = da.SearchCursor(origin_table, fields)
            else:
                origin_cursor = da.SearchCursor(origin_table, fields, filter)

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

    def query(self, table, fields = "*", filter = None, geometry = False) :
        return self._search_da(table, fields, filter, geometry)

    def add(self, table, fields, values) :
        origin_table = os.path.join(self.workspace_path, table)
        table_fields = arcpy.ListFields(origin_table)
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
        edit.startEditing(with_undo=True, multiuser_mode=True)
        edit.startOperation()

        cursor = da.InsertCursor(origin_table, fields)

        inserted_id = []
        for row in values:
            id = cursor.insertRow(row)
            inserted_id.append(id) 

        del cursor
        edit.stopOperation()
        edit.stopEditing(save_changes=True)        

        register = self.query(table, "*", "{} = {}".format(oid_field, inserted_id[0]))
        return register

    def update(self, table, fields, values, filter = None) :
        origin_table = os.path.join(self.workspace_path, table)

        edit = da.Editor(self.workspace_path)
        edit.startEditing(with_undo=True, multiuser_mode=True)
        edit.startOperation()

        if filter:
            cursor = da.UpdateCursor(origin_table, fields, filter)
        else :
            cursor = da.UpdateCursor(origin_table, fields)
        
        for row in cursor:
            for field in fields:
                index = fields.index(field)
                row[index] =values[index]
            cursor.updateRow(row)

        edit.stopOperation()
        edit.stopEditing(save_changes=True)