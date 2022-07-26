 # BIOBLOCKCHAIN
 The goal of my thesis was to design decentralized biometric system, that would be able to ensure that the matching and feature extraction components are not executed on their own. Using the blockchain as an interface for the transmission of operational data, secure the communication ``channels" connected with those components as well. The blockchain can also be used to inspect operations performed in the decentralized biometric system as a way to verify the prerequisite operations, thus securing the channels weak points of biometric system's feature extraction and matching module. 

All modules of the program are implemented in Python language and are documentated dynamically by the Sphinx library, which generates webpages from annotated comments of given classes, functions, or variables. This choice of technologies allows for ease of implementation for the proof-of-concept demonstrator of messages in the proposed system. All modules are written from scratch, using only publicly available standard, cryptographic, or asynchrounous libraries. For ease of use and to guarantee correct versions of the libraries, the program was developed using virtual environment and all required libraries are specified in requirements.txt.

 ## HOW TO RUN
  - python3 -m venv .venv
  - make install -> installs requirements.txt to venv
  - source .venv/bin/activate -> start venv
  - make run -> run simulator script
  - make run_verbose -> run verbose simulator script
  - make tests -> run tests

# DOCUMENTATION
 - enter /docs folder
 - make html
 - open _build/html/index.html
