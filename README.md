# drive-cli

Google Drive on Linux CLI using Python.
Implementing GUI.

## Install

To install the required dependencies and set up the project, follow these steps:

1. Ensure you have [Python](https://www.python.org/downloads/) installed on your system.

2. Clone the repository:

   ```bash
   git clone https://github.com/yohanduartep/drive-cli.git
   cd drive-cli
   ```

3. Create a virtual environment and activate it

4. Install the required Python dependencies:

   ```bash
   googleapi
   dotenv
   ```

5. Create an API from Google Drive on [Google Cloud Console](https://console.cloud.google.com/apis/dashboard).

6. Get your `CLIENT_ID`, `CLIENT_SECRET`, `REDIRECT_URI`, and `REFRESH_TOKEN` from the Google Cloud Console. Create a `.env` file in the project directory and add the following:

   ```bash
   CLIENT_ID=YOUR_ID
   CLIENT_SECRET=YOUR_SECRET
   REDIRECT_URI=YOUR_URI
   REFRESH_TOKEN=YOUR_TOKEN
   ```

7. Run the Python script:

   ```bash
   python drive_cli.py
   ```

8. Use the CLI to interact with your Google Drive:
   - Upload files or folders.
   - List files and folders.
   - Download, delete, or edit files using Neovim.

Enjoy managing your Google Drive from the terminal!
