 # BIOBLOCKCHAIN
The primary objective of my thesis was to identify security vulnerabilities of traditional biometric systems, then design and demonstrate a form of decentralized biometric system that could ensure the autonomous operation of matching(the component that compares the incoming biometric data with the stored data) and feature extraction(component extracts biometric features, e.g. fingerprint scanner) components, which could tackle the identified security issues. To achieve this, I employed blockchain as an interface to facilitate the transmission of operational data(e.g. "features extracted now transmitting to matcher") while concurrently bolstering the security of communication channels linked with these components in distributed network. The blockchain's utilization within the decentralized biometric system serves as a trusted means of prerequisite processes validation thanks to blockchains immutability characteristics, that as a result mitigates the vulnerabilities in the feature extraction and matching modules of the biometric system.

The entirety of the program's modules have been implemented using the Python programming language. These modules are also dynamically documented through the Sphinx library, which generates webpages based on annotated comments associated with classes, functions, and variables. This strategic amalgamation of technologies not only streamlines the process of implementing the proof-of-concept demonstration of messages within the proposed system but also ensures clarity in understanding its functioning.

It's noteworthy that every module has been developed from the ground up, relying solely on publicly available standard, cryptographic, and asynchronous libraries. To ensure a seamless environment and to ascertain the correct versions of these libraries, the program was implemented within a virtual environment. Furthermore, to encapsulate the program's dependencies effectively, all requisite libraries have been listed in the 'requirements.txt' file.

 ## HOW TO RUN
  - python3 -m venv .venv -> creates new empty venv
  - source .venv/bin/activate -> activates created venv
  - make install -> installs requirements.txt into venv
  - make run -> run simulator script with default operation (success enrollment and verification/identification)
  - make tests -> runs unit tests
  - make help -> shows help describing how to run the program with all possible arguments
  
# CLEANUP
  - make clean -> clean the folder
  - deactivate -> deactivates the venv

# HOW TO COMPILE DOCUMENTATION
 - enter /docs folder
 - make html -> compiles the documentation and generates html output into _build
 - open _build/html/index.html -> open documentation in html
 - opem _build/pdf/bioblockchain.pdf -> open documentation in pdf
