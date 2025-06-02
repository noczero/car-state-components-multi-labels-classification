Introduction
---

This repository contains development projects for developing a deep learning model that can recognize physical changes in
a car by analyzing a real-time 3D web interface. 

Starting from build datasets, train classifier model, fine-tune vision language model, 
develop backend application, and develop single page applications.

## Demo 
- Car State Components Classifier App

https://github.com/user-attachments/assets/ae2c1058-c624-48d6-b58e-bf7ef2d734a7

- Car State Components Explainer App

<img width="1912" alt="Screenshot 2025-06-02 at 23 21 27" src="https://github.com/user-attachments/assets/2e11c140-317c-4a1c-8749-7deb2bac3f36" />


## Installation
### Prerequisites

- Python 3.12
- Node.js v20.17.0

### Steps

1. Clone repository.
    ```bash
    git clone git@github.com:noczero/car-state-components-multi-labels-classification.git
    cd car-state-components-multi-labels-classification
    ```
   
2. Install dependencies
   - Backend
       ```bash
       pip install -r requirements.txt
      ```  
   - Classifier App and Explainer App
        ```bash 
     cd www/apps/classifier
      npm install  
     ```
     
      ```bash 
     cd www/apps/explainer
      npm install  
     ```
     
3. Setup environment variables.
    
    Create a `.env` file in the project root directory from `.env.example`
    
   ```bash
      cp .env.example .env
    ```

## Usage
1. Run all services using script.

    ```bash
    ./scripts/start_services.sh    
    ```

2. Open Apps using browser.

   - Classifier App on [localhost:8080](http://localhost:8080)
   
   - Explainer App on [localhost:8082](http://localhost:8082)

3. OpenAPI documentation for backend service on [localhost:8081/docs](http://localhost:8081/docs)

## Troubleshooting Guide

This guide helps resolve common issues encountered during the setup and operation of the Car Components Multi-Labels Classification project.

### 1. Installation Issues

**Problem: `git clone` fails.**
* **Solution:**
    * Ensure you have `git` installed on your system. You can check by running `git --version`. If not installed, download and install it from [git-scm.com](https://git-scm.com/).
    * Verify your internet connection.
    * Check if the repository URL `https://github.com/noczero/car-state-components-multi-labels-classification.git` is correct and accessible.

**Problem: Python version mismatch or `pip` command not found.**
* **Solution:**
    * Verify your Python version by running `python --version` or `python3 --version`. This project requires Python 3.12.
    * If you have multiple Python versions, ensure you are using the correct one or consider using a virtual environment (e.g., `venv`, `conda`).
        ```bash
        # Example for creating and activating a venv
        python3 -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        ```
    * Ensure `pip` is installed and upgraded for your Python 3.12 installation: `python3 -m ensurepip --upgrade` and `python3 -m pip install --upgrade pip`.

**Problem: `pip install -r requirements.txt` fails.**
* **Solution:**
    * **Check Python Version:** Ensure you are using Python 3.12, as specified in the prerequisites. Some dependencies might be version-specific.
    * **Internet Connection:** Verify your internet connection as `pip` needs to download packages.
    * **Permissions:** On some systems, you might need administrator/sudo privileges to install packages globally, though using a virtual environment is highly recommended to avoid this.
    * **Corrupted `requirements.txt`:** Ensure the `requirements.txt` file is not corrupted and is in the correct format.
    * **Specific Package Errors:** If the installation fails on a specific package:
        * Note the error message. It often indicates missing system dependencies (e.g., C compilers, development libraries). For example, on Debian/Ubuntu, you might need `build-essential`, `python3-dev`.
        * Try installing the problematic package individually: `pip install <package-name>`.
        * Search for the error message online for specific solutions related to that package.
    * **Outdated `pip` or `setuptools`:** Try upgrading them:
        ```bash
        pip install --upgrade pip setuptools wheel
        ```

**Problem: Node.js version mismatch or `npm` command not found.**
* **Solution:**
    * Verify your Node.js version by running `node -v`. This project requires Node.js v20.17.0.
    * If you have a different version, consider using a Node version manager like `nvm` to install and switch to the required version.
        ```bash
        # Example using nvm
        nvm install 20.17.0
        nvm use 20.17.0
        ```
    * Ensure `npm` (which comes with Node.js) is in your system's PATH.

**Problem: `npm install` fails in `www/apps/classifier` or `www/apps/explainer`.**
* **Solution:**
    * **Navigate to Correct Directory:** Ensure you are in the correct directory (`www/apps/classifier` or `www/apps/explainer`) before running `npm install`.
    * **Node.js and npm Version:** Double-check that Node.js v20.17.0 and its corresponding npm version are being used.
    * **Internet Connection:** `npm` needs to download packages from the npm registry.
    * **Permissions:** Similar to `pip`, you might encounter permission issues if not using `nvm` or if installing globally.
    * **Cache Issues:** Try clearing the npm cache and reinstalling:
        ```bash
        npm cache clean --force
        rm -rf node_modules package-lock.json  # or del node_modules package-lock.json on Windows
        npm install
        ```
    * **Specific Package Errors:** Look at the error messages. They might indicate incompatibilities or missing peer dependencies. Search online for solutions related to the specific failing package.
    * **Network Issues/Firewall:** If you are behind a corporate firewall, you might need to configure npm to use a proxy.

### 2. Environment Variable Issues

**Problem: `.env` file not found or not working.**
* **Solution:**
    * Ensure you have copied `.env.example` to `.env` in the **project root directory**:
        ```bash
        cp .env.example .env
        ```
    * Verify that the `.env` file contains all necessary environment variables as defined in `.env.example` and that their values are correctly set.
    * Ensure the application is correctly configured to load variables from the `.env` file (e.g., using a library like `python-dotenv` for the backend).
    * Some operating systems or tools might require a restart of the terminal or services after creating/modifying the `.env` file.

**Problem: Application behaves unexpectedly due to incorrect environment variable values.**
* **Solution:**
    * Double-check the values in your `.env` file for typos or incorrect paths/ports/credentials.
    * If the backend or frontend applications provide logging, check the logs for errors related to environment variable loading or usage.
    * Ensure there are no conflicts with system-wide environment variables of the same name if the application isn't correctly prioritizing `.env` files.

### 3. Service Startup Issues

**Problem: `./scripts/start_services.sh` script fails or services do not start.**
* **Solution:**
    * **Script Permissions:** Ensure the script has execute permissions:
        ```bash
        chmod +x ./scripts/start_services.sh
        ```
    * **Interpreter:** The script likely starts with a shebang (e.g., `#!/bin/bash`). Ensure this interpreter is installed and available in your PATH.
    * **Individual Service Failures:** The script might try to start multiple services (backend, classifier app, explainer app). If it fails, try to identify which service is causing the issue.
        * Look at the output of the script for error messages.
        * Try running the commands within the script manually, one by one, to isolate the problem. For example, how the backend is started (e.g., `python app.py` or `uvicorn main:app`) and how the frontend apps are started (e.g., `npm start` or `npm run dev` from their respective directories).
    * **Port Conflicts:** If a service fails to start, it might be because the port it's trying to use (e.g., 8080, 8081, 8082) is already in use by another application.
        * Use tools like `netstat` or `lsof` to check for port usage:
            ```bash
            # On Linux/macOS
            sudo lsof -i :8080
            sudo netstat -tulnp | grep 8080

            # On Windows
            netstat -ano | findstr "8080"
            ```
        * If a port is in use, stop the conflicting application or change the port for your service in its configuration (and update the `.env` file and documentation if necessary).
    * **Log Files:** Check for log files generated by the backend or frontend applications. They often contain detailed error messages. The location of these logs depends on how the applications are configured.

### 4. Application Access Issues

**Problem: Cannot open Classifier App (localhost:8080) or Explainer App (localhost:8082) in the browser.**
* **Solution:**
    * **Services Running:** Confirm that the respective services (Classifier frontend, Explainer frontend) were started successfully by the `./scripts/start_services.sh` script or by running them manually. Check your terminal output for confirmation messages like "Compiled successfully" or "Server running on port...".
    * **Correct URL:** Ensure you are using the correct URL, including `http://` and the correct port.
    * **Firewall:** Your system's firewall or any antivirus software might be blocking access to these ports. Check their settings and create exceptions if necessary.
    * **Browser Cache/Extensions:** Try accessing the app in an incognito/private browsing window or a different browser to rule out issues with browser cache or extensions.
    * **Console Errors:** Open the browser's developer console (usually by pressing F12) and check for any errors in the "Console" or "Network" tabs. These can provide clues about what's going wrong (e.g., failing to load JavaScript files, API errors).

**Problem: OpenAPI documentation (localhost:8081/docs) is not accessible or shows errors.**
* **Solution:**
    * **Backend Service Running:** Verify that the backend service is running correctly on port 8081. Check the terminal output where you started the services.
    * **Correct URL:** Ensure you are using `http://localhost:8081/docs`.
    * **Backend Errors:** Check the backend service's logs for any startup errors or errors related to generating the OpenAPI documentation (e.g., issues with FastAPI or the library used for docs).
    * **Firewall:** Similar to the frontend apps, check firewall settings.

### 5. Model or Backend Logic Issues

**Problem: The 3D web interface is not loading or displaying correctly.**
* **Solution:**
    * **Browser Compatibility:** Ensure you are using a modern web browser that supports WebGL and the technologies used for the 3D interface.
    * **Graphics Drivers:** Outdated or faulty graphics drivers can cause issues with 3D rendering. Try updating your graphics drivers.
    * **Frontend Console Errors:** Check the browser's developer console for JavaScript errors related to the 3D rendering library or data loading.
    * **Backend API Issues:** The 3D interface might depend on data from the backend. Use the browser's Network tab to check if API calls to the backend (likely on port 8081) are succeeding. If they are failing, check the backend logs.

**Problem: Model predictions are incorrect or the application crashes during model inference.**
* **Solution:**
    * **Input Data:** Ensure the input data being fed to the model (e.g., from the 3D interface or uploaded files) is in the expected format and range.
    * **Model Files:** Verify that the trained model files are correctly loaded by the backend. Check paths in the `.env` file or application configuration.
    * **Resource Limits:** Deep learning models can be resource-intensive (CPU, GPU, RAM). If the system is running out of resources, the application might crash or perform poorly. Monitor system resource usage.
    * **Backend Logs:** Check the backend logs for detailed error messages from the model inference code (e.g., TensorFlow, PyTorch errors).
    * **Dependency Versions:** Incompatibilities between deep learning library versions (e.g., TensorFlow, CUDA, cuDNN) can lead to runtime errors. Ensure all related dependencies are compatible, as specified or implied by `requirements.txt`.

**Problem: "Physical changes in a car" are not being recognized correctly.**
* **Solution:**
    * This is more of a model performance issue than a technical bug.
    * **Dataset Quality:** The model's performance heavily depends on the quality and diversity of the training dataset.
    * **Model Training:** Review the model training process, hyperparameters, and evaluation metrics.
    * **Fine-tuning:** If using a vision-language model, the fine-tuning process is critical.
    * **Explainer App:** Use the Explainer App (localhost:8082) to understand model decisions and identify areas for improvement. This app is specifically designed to help debug and interpret model behavior.

### General Troubleshooting Tips

* **Read Error Messages Carefully:** Error messages are your best friends. Read them thoroughly, as they often point directly to the source of the problem.
* **Check Logs:** Backend, frontend (browser console), and service startup logs are invaluable for diagnosing issues.
* **Isolate the Problem:** If multiple components are involved, try to determine which one is failing (e.g., is it the frontend, the backend API, or the model itself?).
* **Reproduce Systematically:** Try to find a consistent way to reproduce the error. This makes it easier to test solutions.
* **Search Online:** Copy and paste specific error messages into a search engine. It's likely someone else has encountered a similar issue.
* **Consult Project Issues:** Check the GitHub repository's "Issues" tab to see if the problem has already been reported or resolved.

If you encounter an issue not covered here, please consider [opening an issue](https://github.com/noczero/car-components-multi-labels-classification/issues) on the GitHub repository with detailed information, including:
* Steps to reproduce the error.
* Full error messages and stack traces.
* Your operating system, Python version, Node.js version.
* Any relevant screenshots.
