FROM jupyter/scipy-notebook

RUN rmdir work

COPY jupyter_notebook_config.py $HOME/.jupyter/
COPY work/Police_Incident_Reports.csv .

