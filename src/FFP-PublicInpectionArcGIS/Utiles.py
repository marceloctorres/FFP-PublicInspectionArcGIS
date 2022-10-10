# -*- coding: utf-8 -*-

from psutil import WINDOWS

if WINDOWS: 
  import arcpy

import logging
import sys
import os
import json

from datetime import datetime
from os import path
from logging import handlers

#### CONSTANTES ######
CONFIG_PATH = ""
LOG_PATH = ""
LOG_FILE = ""

ARCGIS_HANDLER = 1
STREAM_HANDLER = 2
FILE_HANDLER = 4

class ToolboxLogger :

  _logger = None

  @classmethod
  def log_method(cls, func) :
    cls.indent = ""
    cls.indentSize = 2

    def inner(*args, **kwargs) :
      cls._logger.debug("{}-->{}".format(cls.indent, func.__qualname__))
      cls.indent += " ".ljust(cls.indentSize)
      try :
        result = func(*args, **kwargs)
      except Exception as e:
        raise e
      finally :
        cls.indent = cls.indent[:-2]
        cls._logger.debug("{}<--{}".format(cls.indent, func.__qualname__))

      return result
    
    return inner

  @classmethod
  def initLogger(cls, source = "ToolboxLogger", log_path = LOG_PATH, log_file = LOG_FILE, handler_type = ARCGIS_HANDLER) :
    loggerFactory = LoggerFactory()
    cls._logger = loggerFactory.getLogger(source, log_path, log_file, handler_type = handler_type)
    cls.indent = ""
    cls.indentSize = 2

  @classmethod
  def setInfoLevel(cls) :
    cls._logger.logLevel = logging.INFO
    cls._logger.setLevel(logging.INFO)
    cls.info("Level: INFO")
    
    for h in cls._logger.handlers :
      h.setLevel(cls._logger.logLevel)

  @classmethod
  def setDebugLevel(cls) :
    cls._logger.logLevel = logging.DEBUG
    cls._logger.setLevel(logging.DEBUG)
    cls.info("Level: DEBUG")

    for h in cls._logger.handlers :
      h.setLevel(cls._logger.logLevel)

  @classmethod
  def debug(cls, message) :
    cls._logger.debug("%s", "{}{}".format(cls.indent, message))

  @classmethod
  def info(cls, message) :
    cls._logger.info("%s", "{}{}".format(cls.indent, message))

  @classmethod
  def error(cls, message) :
    cls._logger.error("%s", "{}{}".format(cls.indent, message))

  @classmethod
  def warning(cls, message) :
    cls._logger.warging("%s", "{}{}".format(cls.indent, message))


if WINDOWS:
  class ArcGisLogHandler(logging.Handler): 
      def __init__(self): 
          logging.Handler.__init__(self)
          
      def emit(self, record): 
          if record.levelno >= logging.ERROR: 
              log_method = arcpy.AddError 
          elif record.levelno >= logging.WARNING: 
              log_method = arcpy.AddWarning 
          else: 
              log_method = arcpy.AddMessage 
          log_method(self.format(record))

class LoggerFactory : 
  #self.pattern = '%(asctime)s - %(message)s'
  pattern = '%(message)s'

  def clearLogger(self, name) :
    logger = logging.getLogger(name)
    logger.handlers.clear()

  def getLogger(self, name, pathName, fileName, handler_type = ARCGIS_HANDLER) :
    self.logLevel = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(self.logLevel)

    if len(logger.handlers) > 0:  

      if handler_type & FILE_HANDLER == FILE_HANDLER:
        if not any(map(lambda h : h.__class__.__name__ == "RotatingFileHandler", logger.handlers)) :
          self.addRotatingFileHandler(logger, pathName, fileName)
        
      if WINDOWS and (handler_type & ARCGIS_HANDLER == ARCGIS_HANDLER):
        if not any(map(lambda h : h.__class__.__name__ == "ArcGisLogHandler", logger.handlers)) :
          self.addArcGisLogHandler(logger)

      if handler_type & STREAM_HANDLER == STREAM_HANDLER:
        if not any(map(lambda h : h.__class__.__name__ == "StreamHandler", logger.handlers)) :
            self.addStreamHandler(logger)
    else:
      if handler_type & FILE_HANDLER == FILE_HANDLER:
        self.addRotatingFileHandler(logger, pathName, fileName)
      
      if WINDOWS and (handler_type & ARCGIS_HANDLER == ARCGIS_HANDLER):
        self.addArcGisLogHandler(logger)

      if handler_type & STREAM_HANDLER == STREAM_HANDLER:
        self.addStreamHandler(logger)

    return logger

  def addRotatingFileHandler(self, logger, pathName, fileName) :
    fullFileName = os.path.join(pathName, "{}{}.log".format(fileName, datetime.now().strftime("%Y%m%d%H%M")))
    chs = handlers.RotatingFileHandler(filename = fullFileName, backupCount = 52, maxBytes = 1000000, encoding='utf-8')
    chs.setFormatter(logging.Formatter(self.pattern))
    chs.setLevel(self.logLevel)
    logger.addHandler(chs)
    logger.debug("Agregando RotatingFileHandler")
  
  def addStreamHandler(self, logger) :
      ch = logging.StreamHandler(sys.stdout)                             
      ch.setFormatter(logging.Formatter(self.pattern))
      ch.setLevel(self.logLevel)
      logger.addHandler(ch)
      logger.info("Agregando StreamHandler")

  def addArcGisLogHandler(self, logger) :
    if WINDOWS: 
      ch = ArcGisLogHandler()
      ch.setFormatter(logging.Formatter(self.pattern))
      ch.setLevel(self.logLevel)
      logger.addHandler(ch)
      logger.info("Agregando ArcGisLogHandler")
    else :
      pass

class Configuracion:

    def __init__(self, configPath):        
        try:
            _path = os.path.dirname(os.path.abspath(__file__))
            if(configPath == None) :
              self.path = CONFIG_PATH
            else :
              self.path = configPath

            _file = open(self.path, encoding='utf-8')
            config = _file.read()
            
            self.configs = json.loads(config)

        except Exception as d:
            self.WriteMessage("Archivo de configuracion no es válido, {}".format(str(d)))
            raise d

    def getConfigKey(self, key):
        try:
          value = self.configs[key]
          return value
        except Exception as d:            
          self.WriteMessage("La llave ''{}'' no existe.\n{}".format(key, str(d)))
          pass
            
    def WriteMessage(self, msg) :
        ToolboxLogger.info(msg)    

class JsonFile :

  @staticmethod
  def readFile(filename):
    records = []

    if os.path.exists(filename): 
      try :
        with open(filename, encoding='utf-8') as f:
          text = f.read()
          records  = json.loads(text)
      except :
        records = []
    return records

  @staticmethod
  def writeFile(filename, records) :
    with open(filename, 'w') as f:
      text = json.dumps(records, indent = 4)
      f.write(text)

class TimeUtil :

  startTime = None
  endTime = None 
  timeSpan = None

  def __init__(self) :
    self.initTimer()

  def initTimer(self) :
    self.startTime  = datetime.now()

  def stopTimer(self) :
    self.endTime = datetime.now()
    self.timeSpan = self.endTime - self.startTime
    return self.timeSpan

  @staticmethod
  def nowCode() :
    return datetime.now().strftime("%Y%m%d%H%M%S")
