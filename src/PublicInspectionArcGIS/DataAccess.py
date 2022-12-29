# -*- coding: utf-8 -*-

DEFAULT_OPERATOR = "="

class QueryFilter:
    def __init__(self, query_filter) :
        self._query_filter = query_filter

    def getWhereClause(self) :
        def __process_clausule(item) : 
            fields = []
            values = []
            operators = []
            connectors = []

            field = item["query"]["field"]
            value = item["query"]["value"] if "value" in item["query"] else None
            operator = item["query"]["operator"] if "operator" in item["query"] else None
            connector = item["connector"] if "connector" in item else None
            queries = item["queries"] if "queries" in item else []
            for query in queries:
               f, v, o, c, cf, cv, co, cc = __process_clausule(query)
               fields.append(f)
               values.append(v)
               operators.append(o)
               connectors.append(c)

               if cf != [] :
                   fields.append(cf)
               if cv != [] :
                   values.append(cv)
               if co != [] :
                   operators.append(co)
               if cc != [] :
                   connectors.append(cc)

            return field, value, operator, connector, fields, values, operators, connectors

        fields = []
        values = []
        operators = []
        connectors = []
        for item in self._query_filter["queries"] :
            f, v, o, c, cf, cv, co, cc = __process_clausule(item)
            fields.append(f)
            values.append(v)
            operators.append(o)
            connectors.append(c)
            if cf != [] :
                fields.append(cf)
            if cv != [] :
                values.append(cv)
            if co != [] :
                operators.append(co)
            if cc != [] :
                connectors.append(cc)

        return DataAccess.getWhereClause(fields, values, operators, connectors)

class QueryItem :
    def __init__(self, field, values, operator = None): 
        self._field = field
        self._values = values
        self._operator = operator

    def getWhereClause(self) :
        return DataAccess.getWhereClause(self._field, self._values, self._operator)

class QueryList :
    def __init__(self) :
        self._queries = []

    def addQuery(self, queryItem, connector = None) :
        if isinstance(queryItem._field, list) and isinstance(queryItem._values, list):
            index = 0
            for f in queryItem._field :
                v = queryItem._values[index]
                o = queryItem._operator[index] if queryItem._operator else None
                self._queries.append({"item": QueryItem(f, v, o), "connector": connector})
                index += 1
        else: 
            self._queries.append({"item": queryItem, "connector": connector})

    def getWhereClause(self):
        if len(self._queries) > 0 :
            fields = list(map(lambda q : q["item"]._field, self._queries))
            values = list(map(lambda q : q["item"]._values, self._queries))
            operators = list(map(lambda q : q["item"]._operator if q["item"]._operator else None, self._queries))
            connectors = list(map(lambda  q: q["connector"] if q["connector"] else "", self._queries))

            return DataAccess.getWhereClause(fields, values, operators, connectors)
        else :
            return None

class DataAccess :

    @classmethod
    def _getPartialWhereClause(cls, field, value, operator = None, connectors = None):
        if isinstance(field, list) and isinstance(value, list) :
            if not operator :
                operator = []
                for f in field:
                    operator.append(None)
            if not connectors :
                connectors = []
                for f in field:
                    connectors.append(None)

            where = cls._getWhereClauseMulti(field, value, operator, connectors)

        elif isinstance(value, list):
            value = list(map(lambda v: "'{}'".format(v) if isinstance(v, str) else "{}".format(v), value))
            where = "{} in ({})".format(field, ", ".join(value))
        elif isinstance(value, str): 
            if not operator :
                operator = DEFAULT_OPERATOR
            if "NULL" in value.upper():
                where = "{} {} {}".format(field, operator, value) if value else "{} {} ''".format(field, operator)
            else:
                where = "{} {} '{}'".format(field, operator, value) if value else "{} {} ''".format(field, operator)
        else:
            if not operator :
                operator = DEFAULT_OPERATOR
            where = "{} {} {}".format(field, operator, value) if value else "{} {} ''".format(field, operator)
        return where

    @classmethod
    def getWhereClause(cls, field, value, operator = None, connectors = None):
        if isinstance(field, str):
            return cls._getPartialWhereClause(field, value, operator)

        if isinstance(field, list) and isinstance(value, list) :
            return cls._getWhereClauseMulti(field, value, operator, connectors)

        return ""
    
    @classmethod
    def _getWhereClauseMulti(cls, fields, values, operators = None, connectors = None) :
        if len(fields) <= len(values):
            if not operators:
                operators = []

            if len(operators) < len(fields) :
                count = len(fields) - len(operators)
                index = 0
                while index < count :
                    index += 1
                    operators.append(None)

            if not connectors:
                connectors = []

            if len(connectors) < len(fields) :
                count = len(fields) - len(connectors)
                index = 0
                while index < count :
                    index += 1
                    connectors.append(None)
                
            if operators and connectors:
                clauses = list(map(cls._getPartialWhereClause, fields, values, operators, connectors))
            else :
                clauses = list(map(cls._getPartialWhereClause, fields, values))
            
            emptyValues = [c for c in clauses if c == ""]
            if len(emptyValues) < 1 :
                if len(clauses) == 1:
                    return clauses[0]
                elif not connectors:
                    where = " AND ".join(clauses)
                    return "({})".format(where.strip())
                else :
                    if len(connectors) == len(clauses):
                        connectors.pop()
                    where = ""
                    i = 0
                    for clause in clauses:
                        if i >= len(connectors) :
                            connector = ""
                        elif not connectors[i] :
                            connector = "AND"
                        else :
                            connector = connectors[i]
                        where += "{} {} ".format(clause, connector.strip())
                        i += 1
                    return "({})".format(where.strip())
                        
        return ""

    @classmethod
    def enumElements(self, elements):
        element_list = []
        if elements:
            if isinstance(elements, list) :
                for element in elements:
                    if not isinstance(element, list) :
                        element_list.append(element)
                    else :
                        sub_list = self.enumElements(element)
                        element_list = element_list + sub_list
            else :
                element_list.append(elements)
        return element_list

    def __init__(self) :
        pass

    def search(self, table, fields, filter = None) :
        pass

    def update(self, tbl_destino, campo_busqueda, campos, registro_origen, valor_relacion, tipo_operacion) :
        pass