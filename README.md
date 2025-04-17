# Simultaneous File Transfer System

A modern cross-platform application for transferring files between multiple computers simultaneously with a clean graphical user interface built with Python and Tkinter.

## Overview

This application allows users to send files to multiple destinations at once or receive files through a simple, intuitive interface. It displays the user's IP address prominently to facilitate connections between computers and provides real-time progress tracking for all transfers.

## Features

- **Dual Operation Modes**: Run as either client (sender) or server (receiver)
- **Simultaneous Transfers**: Send files to multiple destinations concurrently
- **Real-time Progress Tracking**: Monitor transfer progress with visual indicators
- **Modern UI**: Clean interface with intuitive controls
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Transfer Statistics**: View speed, time, and file size metrics in real-time
- **No External Dependencies**: Built with standard Python libraries

## Requirements

- Python 3.6 or higher

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/SuyashAlphaC/Simultaneous-File-Transfer.git
   ```

2. Navigate to the project directory:
   ```
   cd Simultaneous-File-Transfer
   ```

3. Run the application:
   ```
   python file_transfer.py
   ```

## Usage

### Starting the Application

Run `file_transfer.py` to open the startup screen where you can select your desired mode:

```
python file_transfer.py
```

The startup screen displays your IP address and offers two operation modes:

### Client Mode (Sending Files)

1. Select "Client Mode" from the startup screen
2. Click "Browse" to select a file to send
3. Enter target IP addresses (one per line) in the text area
4. Click "Send File" to begin transfers
5. Monitor progress for each receiving server

### Server Mode (Receiving Files)

1. Select "Server Mode" from the startup screen
2. The server starts automatically and begins listening for connections
3. Received files are saved to the "received_files" directory by default
4. The log window displays transfer status and details

## Configuration

### Changing Default Port

The default port is 5000. To change it, modify the `port` parameter in:
- `FileTransferClient.send_file()` method
- `FileReceiveServer` initialization

### Changing Save Directory

Default save location is "received_files". To change it:
- Modify the `save_directory` parameter when initializing `FileReceiveServer`

## Troubleshooting

### Connection Issues

- Ensure the server is running before initiating transfers
- Check firewall settings to allow connections on port 5000
- Verify both computers are on the same network

### Performance Issues

- Large files may take significant time to transfer
- Network congestion affects transfer speeds
- Multiple simultaneous transfers will share available bandwidth

## Technical Details

### Network Protocol

The application uses TCP sockets with a simple protocol:
1. Connection establishment
2. Filename transmission
3. File size transmission
4. File data transmission in 4KB chunks

### Component Architecture

- **StartupSelector**: Mode selection UI
- **FileTransferClient**: Handles sending files
- **FileReceiveServer**: Manages incoming transfers
- **Custom UI Components**: Styled interface elements

## Future Enhancements

- File transfer encryption
- Automatic server discovery
- Transfer queue management
- Resume interrupted transfers
- Multiple file selection
- Drag and drop interface
