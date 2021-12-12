# SQLPATCH:  Towards Bug Detection, Rectification and Evolution in SQL Database Engines



## Introduction

SQLPatch is the first infrastructure to automatically detect and repair SQLite vulnerabilities, and can analyze the evolution of vulnerabilities based on the results. 



## Structure

- **code**    [README there]() has details for usage.
  - **util**  Components of SQLPATCH, including frontend module, analysis module, automatic rectification module, verification module, etc. 
- **config**  Configuration file
  - **configure.json**：Configure the information of the project to be fixed. 
  - **patch_template.json**: Patch template list
- **corpus**  SQLite source code
- **output**  The repaired code and its repair report
- **statistics**  Charts used in the paper



## Environment

You need at least the following dependencies:

- **Infer**

  Our tecnique is built on top of the open source *Infer v1.1.0* static analyzer. 

  On Mac, the simplest way is to use [Homebrew](http://brew.sh/). Type this into a terminal:

  ```
  brew install infer
  ```

  On Linux, or if you do not wish to use Homebrew on Mac, use our latest [binary release](https://github.com/facebook/infer/releases/latest). Download the tarball then extract it anywhere on your system to start using infer. For example, this downloads infer in /opt on Linux (replace `VERSION` with the latest release, eg `VERSION=1.0.0`):

  ```shell
  VERSION=0.XX.Y; \
  curl -sSL "https://github.com/facebook/infer/releases/download/v$VERSION/infer-linux64-v$VERSION.tar.xz" \
  | sudo tar -C /opt -xJ && \
  sudo ln -s "/opt/infer-linux64-v$VERSION/bin/infer" /usr/local/bin/infer
  ```

  If the binaries do not work for you, or if you would rather build infer from source, follow the [install from source](https://github.com/facebook/infer/blob/main/INSTALL.md#install-infer-from-source) instructions to install Infer on your system.

  Maybe other versions are also available, but we recommend *Infer v1.1.0* .

  For more details, please refer to the [official documentation](https://fbinfer.com/docs/getting-started)

  

- **Python**

  The version of Python we used is *3.9.5*. Maybe other versions are also available, we recommend that your Python version is as high as 3.7 or above. 

  

## Usage

- #### configuration

  We recommend that you understand the role of the following two configuration files before using. 

  We have also attached examples of these two configuration files in the folder `./config/` for your reference. 

  **1. Project information**

  In configuration file `./config/configure.json`, you can configure the download link and name of the version of SQLite you need. 

  For example, the information of a single project corpus in the configuration file is as follows：

  ```json
  {
      "project_name": "sqlite-3.37",
      "download_url": "https://www.sqlite.org/src/tarball/bd41822c/SQLite-bd41822c.tar.gz"
    }
  ```

  

  **2. Patch template**

  SQLPatch is extensible and allows developers to provide custom patch templates, it's easy to adapt SQLPatch to handle some special cases. 

  In order to avoid the situation that some aggressive rectification affect the original function of the project to be rapaired, also in order to fix some vulnerabilities not covered by the default repair strategy, you can configure the file `./config/patch_template.json` to specify the location of specific patches or skip some false positive vulnerabilities as appropriate.

  

  For example, the information of a single project corpus in the configuration file is as follows：

  ```json
  {
          "file" : "sqlite3.c",				//the path of the file to be repaired
          "line" : 86151,						//the error line
          "bug_type" : "NULL_DEREFERENCE",	//the type of vulnerability
          
          "poniter_name": "null",				//the name of the related variable name
          "strategy" : "skip",				//the repair strategy (skip or offset)
          "project_name" : "sqlite-3.15",		//the project it belongs to
          "offset" : 0						//the offset line number of the patch
      }
  ```

  

- #### Fully automatic process

  You can change various configurations in above two files as you need, then run the following commands in `./code` 

  ```shell
  python3 main.py
  ```

  It will automatically complete the download, preprocessing, vulnerability analysis, rectification, and verification of the specified project to be repaired. Then it output the repaired project and its corresponding detection and repair reports to the folder `./output/`









 













