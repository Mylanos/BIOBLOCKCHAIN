 # BIOBLOCKCHAIN
 The goal of my thesis was to design decentralized biometric system, that would be able to ensure that the matching and feature extraction components are not executed on their own. Using the blockchain as an interface for the transmission of operational data, secure the communication ``channels" connected with those components as well. The blockchain can also be used to inspect operations performed in the decentralized biometric system as a way to verify the prerequisite operations, thus securing the channels weak points of biometric system's feature extraction and matching module. 

All modules of the program are implemented in Python language and are documentated dynamically by the Sphinx library, which generates webpages from annotated comments of given classes, functions, or variables. This choice of technologies allows for ease of implementation for the proof-of-concept demonstrator of messages in the proposed system. All modules are written from scratch, using only publicly available standard, cryptographic, or asynchrounous libraries. For ease of use and to guarantee correct versions of the libraries, the program was developed using virtual environment and all required libraries are specified in requirements.txt.

 ## HOW TO RUN
  - python3 -m venv .venv -> creates new empty venv
  - make install -> installs requirements.txt into venv
  - source .venv/bin/activate -> activates created venv
  - make run -> run simulator script with default operation (success enrollment and verification/identification)
  - make tests -> runs unit tests
  - make help -> shows help describing how to run the program with all possible arguments
  
# CLEANUP
  - make clean -> clean the folder
  - deactivate -> deactivates the venv

# HOW TO COMPILE DOCUMENTATION
 - enter /docs folder
 - make html
 - open _build/html/index.html
