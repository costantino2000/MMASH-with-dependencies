## MMASH: Multilevel Monitoring of Activity and Sleep in Healthy people - Data reading and analysis - fork with scripts to preprocess and test the data

Tested on Windows 11 23H2 with VSCode. Instructions for the requirements:

- Download and install [Python 3.8.10](https://www.python.org/downloads/release/python-3810/);
- Create a virtual environment with [```venv```](https://docs.python.org/3/library/venv.html) and activate it (change the name in the gitignore if you don't call it venv);
- From the terminal and with the virtual environment active install the requirements with ```pip install -r requirements.txt```;
- Download the dataset from [here](https://physionet.org/files/mmash/1.0.0/MMASH.zip?download) and extract the ```DataPaper``` folder inside the Workspace folder.

You can now run the notebook ```Code_MMASH.ipynb``` on Jupyter after selecting the created virtual environment for the kernel.


### Preprocessing and model training

This fork adds three main scripts (made by me and [@CongiuPietroMassimo](https://github.com/CongiuPietroMassimo), the script ```extract_sleep_features``` was made by [@eleonoraPorcu](https://github.com/Mowgly27) and [@silviam-massa](https://github.com/silviam-massa) and adapted to work with the rest):

- ```1_Preprocess_all``` to create the files ending in ```-processed``` in the datasets folders;
- ```2_Create_datasets``` to create the train sets in the ```Dataset``` folder;
- ```3_Test_models``` to run various tests and get results (the metrics for the feature selection need to be changed in ```models_testing```).

Every other script in the Workspace folder is called by them, after extracting the ```DataPaper``` folder you can just run the main scripts sequentially and get the outputs.


## Original README

#### Rossi, A.<sup>1</sup>, Da Pozzo, E.<sup>2</sup>, Menicagli, D.<sup>3</sup>, Tremolanti, C.<sup>2</sup>, Priami, C.<sup>1,4</sup>, Sirbu, A.<sup>1</sup>, Clifton, D.<sup>5</sup>, Martini, C.<sup>2</sup>, & Morelli, D.<sup>5,6</sup>

*<sup>1</sup> Department of Computer Science, University of Pisa, Pisa, Italy;
<sup>2</sup> Department of Pharmacy, University of Pisa, Pisa, Italy;
<sup>3</sup> MOMILab, IMT School for Advanced Studies Lucca, Lucca, Italy;
<sup>4</sup> COSBI, Rovereto, Italy;
<sup>5</sup> Department of Engineering Science, University of Oxford, Oxford, UK;
<sup>6</sup> Huma Therapeutics Limited, London, UK.*

---

Multilevel Monitoring of Activity and Sleep in Healthy people (MMASH) dataset provides 24 hours of continuous beat-to-beat heart data, triaxial accelerometer data, sleep quality, physical activity and psychological characteristics (i.e., anxiety status, stress events and emotions) for 22 healthy participants. Moreover, saliva bio-markers (i.e.cortisol and melatonin) and activity log were also provided in this dataset. The MMASH dataset will enable researchers to test the correlations between physical activity, sleep quality, and psychological characteristics.

The Python Notebook provided in this repository is useful to read and analyze MMASH dataset.

---

**Dataset:** Rossi, A., Da Pozzo, E., Menicagli, D., Tremolanti, C., Priami, C., Sirbu, A., Clifton, D., Martini, C., & Morelli, D. (2020). Multilevel Monitoring of Activity and Sleep in Healthy People (version 1.0.0). PhysioNet. https://doi.org/10.13026/cerq-fc86.

**DataPaper link:** https://physionet.org/content/mmash/1.0.0/
