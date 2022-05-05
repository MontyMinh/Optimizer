# Change Log
All notable changes to this project will be documented in this file.
 
## [0.0.0] - 27-4-2022
 
### Added
 
* GitHub repository for Model 4.0
* [README.md](https://github.com/MontyMinh/Model4.0/blob/main/README.md) with details of improvements of Model 4.0
* [CHANGELOG.md](https://github.com/MontyMinh/Model4.0/blob/main/CHANGELOG.md) and format to match conventional style.
* [Model4](https://github.com/MontyMinh/Model4.0/tree/main/model), the folder holding the Python code for the model, in which there are:
  * [\_\_init\_\_.py](https://github.com/MontyMinh/Model4.0/blob/main/model/__init__.py), init file for the folder, also contains documentation.
  * [preprocessing.py](https://github.com/MontyMinh/Model4.0/blob/main/model/preprocessing.py), file for collecing the data to run the optimization from excel sheets.
  * [optimization.py](https://github.com/MontyMinh/Model4.0/blob/main/model/optimization.py), file for setting up the linear program and optimize.
  * [postprocessing.py](https://github.com/MontyMinh/Model4.0/blob/main/model/postprocessing.py), file for arranging the output data back into Excel.
  * [ui.py](https://github.com/MontyMinh/Model4.0/blob/main/model/ui.py), file for hosting the user interface for interacting with the full optimization program.
  
### Changed
 
### Fixed

## [0.0.1] - 5-5-2022

### Added

* [modeldata.py](https://github.com/MontyMinh/Model4.0/blob/main/model/modeldata.py), file containing a class to store the data generate by the program
* [program.py](https://github.com/MontyMinh/Model4.0/blob/main/model/program.py), file for running the entire optimization program
* [ModelFlow.pdf](https://github.com/MontyMinh/Model4.0/blob/main/docs/ModelFlow.pdf), file detailing the inputs/outputs and dependencies of the different .py files

