# **Honors Thesis Scattering and Absorption Coefficient, AAE, SAE and SSA plots**
## By Andre Bergeron 
## Data source: The University of Utah - Storm Peak Laboratory
## Spring 2026

This repository contains the source code that Andre Bergeron contributed for his Honors thesis analysis and paper. The data folder includes two CSV files with aerosol measurements from two Colorado sites: Storm Peak Laboratory and Table Mountain, both currently in operation. Since completing the honors thesis, this work has continued and was published in the Journal of Atmospheric Chemistry and Physics (see https://doi.org/10.5194/acp-26-6593-2026) on May 18th 2026. The figures included here were edited prior to publication and therefore may not match the final figures presented in the paper.

The repository here can be either cloned or containerized.



If users want to containerize the code, follow these guidelines to properly set up and run the environment.

This repository must first be cloned onto a local machine to gain access to the apporiate workspace environment.

To build the Docker Image, the user should run:

```
docker build -t aopdataprocessing .
```

To run the Docker container, the user should run:

```
docker run -it -p 8888:8888 -v $(pwd):/home/projectuser aopdataprocessing
```
Once the container has been successfully run, the user should attach the container to VScode and select the python environment name "projectuser" in the /home/projectuser directory.
