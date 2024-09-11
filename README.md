# DatSimonBot
My own bot - assistant

## Creating new modules
1. Create a python file in either `dsbMain/modules/stable/` or `dsbMain/modules/experimental/`
2. Create a class with name matching the file name but in PascalCase (It is important for import purposes). It needs to be a subclass of `dsbMain.modules.module.Module`.
