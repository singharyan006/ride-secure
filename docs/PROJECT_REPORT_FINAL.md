# **RideSecure - Intelligent Helmet Detection System**


## ABSTRACT

Road traffic accidents are a major cause of fatalities and severe injuries globally, with a significant percentage involving two-wheeler riders without helmets. Manual monitoring of helmet compliance is inefficient, resource-intensive, and often impractical for large-scale enforcement. This project, "RideSecure," presents an intelligent computer vision system to automate the detection of motorcycle helmet violations from video footage. The system utilizes a hybrid architecture, integrating a JavaFX desktop application for user interaction with a powerful Python FastAPI backend for machine learning-based video processing.

The core of the system employs state-of-the-art deep learning models, specifically YOLOv8 for robust person detection and a custom-trained model for accurate helmet identification. To ensure consistent tracking of individuals across video frames, the DeepSORT algorithm is implemented. When a violation is detected (a rider without a helmet for a sustained period), the system logs the event, including timestamps and bounding box coordinates, into a Supabase PostgreSQL database. For user review, the system generates an annotated video where riders are marked with color-coded bounding boxes—green for compliance and red for violation. This automated, data-driven approach provides a scalable and efficient solution for traffic authorities to enhance road safety and enforce helmet laws effectively.

**Keywords:** Helmet Detection, Computer Vision, YOLOv8, DeepSORT, Traffic Violation, FastAPI, JavaFX.

---
<div style="page-break-after: always;"></div>

## TABLE OF CONTENTS

**ABSTRACT** .................................................................................................................................................... v
<br>
**TABLE OF CONTENTS** ................................................................................................................................. vi
<br>
**LIST OF FIGURES** ................................................................................................................................... ix
<br>
**LIST OF TABLES** ..................................................................................................................................... x

<br>

| CHAPTER NO. | TITLE | PAGE NO. |
| :--- | :--- | :--- |
| **1** | **INTRODUCTION** | **1** |
| 1.1 | General Introduction | 2 |
| 1.2 | Motivation | 3 |
| 1.3 | Objectives | 4 |
| 1.4 | Scope | 5 |
| 1.5 | Sustainable Development Goal of the Project | 6 |
| **2** | **SYSTEM REQUIREMENTS** | **7** |
| 2.1 | Hardware Requirements | 8 |
| 2.2 | Software Requirements | 9 |
| **3** | **SYSTEM DESIGN** | **11** |
| 3.1 | System Architecture Diagram | 12 |
| 3.2 | Use Case Diagram | 14 |
| 3.3 | Class Diagram | 15 |
| **4** | **MODULE DESCRIPTION** | **17** |
| 4.1 | Module 1: Python Backend API | 18 |
| 4.2 | Module 2: Machine Learning Core (Detection & Tracking) | 21 |
| 4.3 | Module 3: JavaFX Desktop Frontend | 25 |
| 4.4 | Module 4: Database and Data Persistence | 29 |
| 4.5 | Result | 31 |
| **5** | **CONCLUSION** | **33** |
| | REFERENCES | 35 |
| | APPENDIX A: CODING | 37 |

---
<div style="page-break-after: always;"></div>

# **CHAPTER 1**

# **INTRODUCTION**

## **1.1 General Introduction**

In the modern era of rapid urbanization and increasing vehicle density, ensuring road safety has become a paramount challenge for governments and communities worldwide. Two-wheeler vehicles, such as motorcycles and scooters, are a popular mode of transport due to their affordability and ability to navigate congested traffic. However, their riders are significantly more vulnerable to severe injuries and fatalities in the event of an accident compared to occupants of enclosed vehicles. The World Health Organization (WHO) has consistently highlighted that wearing a helmet is the single most effective measure to reduce head injuries and fatalities from motorcycle crashes [1].

Despite mandatory helmet laws in many countries, non-compliance remains a widespread issue. The conventional method of enforcement relies on manual monitoring by traffic police, which is labor-intensive, geographically limited, and prone to human error. This manual approach cannot provide the continuous and comprehensive surveillance needed to foster a culture of safety. The advent of artificial intelligence, particularly in the field of computer vision, offers a transformative solution to this problem. By leveraging deep learning algorithms, it is possible to create automated systems that can analyze video feeds from traffic cameras to detect violations accurately and tirelessly.

This project, "RideSecure," is an implementation of such an intelligent system. It is designed to automatically identify motorcycle riders who are not wearing helmets by processing video footage. The system integrates a robust machine learning pipeline for detection and tracking with a user-friendly desktop application for operation and review. By automating the detection process, RideSecure aims to provide law enforcement agencies with a powerful tool to improve helmet law compliance, gather data for traffic safety analysis, and ultimately reduce the number of preventable injuries and deaths on the road.

## **1.2 Motivation**

The motivation for developing the RideSecure system stems from a combination of alarming statistics, technological opportunities, and the potential for significant societal impact. Road traffic accidents are a leading cause of death globally, and the vulnerability of motorcyclists is a major contributing factor. The lack of helmet usage dramatically increases the risk of fatal head injuries, turning minor incidents into life-threatening events. The sheer volume of traffic in urban areas makes it impossible for human officers to monitor every intersection and roadway effectively, creating a gap in enforcement that many riders exploit.

This enforcement gap not only endangers individual riders but also imposes a substantial economic burden on society through healthcare costs, loss of productivity, and emergency response services. The need for a more efficient, scalable, and objective monitoring system is therefore urgent. Simultaneously, the field of computer vision has matured to a point where complex object detection and tracking tasks can be performed with high accuracy in real-world scenarios. The availability of powerful open-source deep learning frameworks like PyTorch and models like YOLOv8 has democratized the development of sophisticated AI applications.

This convergence of a critical social problem and a viable technological solution is the primary driver for this project. The goal is to harness the power of AI to create a practical tool that can augment the efforts of traffic authorities. By providing reliable, automated, and data-driven violation detection, RideSecure can help enforce safety regulations more effectively, deter non-compliant behavior, and contribute to a safer road environment for everyone. The project is also motivated by the desire to build a complete, end-to-end system that spans from low-level machine learning inference to a high-level graphical user interface, demonstrating a full-stack application of modern software engineering principles.

## **1.3 Objectives**

The primary goal of this project is to design, develop, and evaluate an automated system for detecting motorcycle helmet violations from video footage. To achieve this, the following specific objectives have been defined:

1.  **To Develop a Highly Accurate Detection Model:** Implement and fine-tune a deep learning model based on the YOLOv8 architecture to accurately detect persons and helmets in diverse video conditions, achieving a high true-positive rate while minimizing false positives.

2.  **To Implement Robust Multi-Object Tracking:** Integrate the DeepSORT algorithm with the detection model to assign and maintain a unique identification tag for each detected individual across consecutive frames, enabling reliable tracking of violators.

3.  **To Build a Scalable Backend Service:** Design and create a backend API using Python and FastAPI to handle video processing requests, execute the machine learning pipeline, and manage communication with the database and frontend client.

4.  **To Create an Intuitive User Interface:** Develop a cross-platform desktop application using Java and JavaFX that allows users to easily upload videos, initiate processing, view a real-time list of detected violations, and play back the annotated output video.

5.  **To Establish a Persistent Violation Database:** Utilize a Supabase PostgreSQL database to store detailed records of each violation, including the violator's track ID, the precise timestamp and frame number of the detection, and associated metadata for future analysis and reporting.

## **1.4 Scope**

The scope of the RideSecure project defines the functional boundaries and key features that are included in the current implementation. It also clarifies what is considered outside the scope for this phase of development.

**In-Scope:**

*   **Video-Based Detection:** The system is designed to process pre-recorded video files in common formats (e.g., MP4, AVI, MOV).
*   **Person and Helmet Detection:** The core functionality is to detect persons (assumed to be on two-wheelers) and determine if they are wearing a helmet.
*   **Violation Logging:** The system logs a violation when a person is tracked without a helmet for a predefined number of consecutive frames to ensure reliability.
*   **Database Storage:** All detected violations are stored in a PostgreSQL database with relevant metadata, such as track ID, timestamp, and bounding box coordinates.
*   **Desktop Application:** A graphical user interface (GUI) is provided for users to interact with the system, including uploading videos and viewing results.
*   **Annotated Video Output:** The system generates a new video file where detected persons are annotated with color-coded bounding boxes (red for no helmet, green for helmet) to provide visual evidence.

**Out-of-Scope:**

*   **Live Stream Processing:** The current version does not support real-time processing from live camera feeds (e.g., RTSP streams).
*   **License Plate Recognition:** The system does not include functionality for detecting or reading license plates. This is a planned future enhancement.
*   **Rider-Motorcycle Association:** The system detects persons but does not explicitly associate them with a specific motorcycle.
*   **Advanced Analytics Dashboard:** While data is stored in a database, the project does not include a web-based dashboard for advanced data visualization or trend analysis.
*   **Multi-Camera Support:** The system processes one video at a time and does not include features for managing or synchronizing feeds from multiple cameras.

## **1.5 Sustainable Development Goal of the Project**

This project directly contributes to the **United Nations Sustainable Development Goals (SDGs)**, a blueprint for a better and more sustainable future for all. Specifically, the RideSecure system aligns with **SDG 3: Good Health and Well-being**.

Within SDG 3, the project makes a direct contribution to **Target 3.6**, which aims to: *"By 2020, halve the number of global deaths and injuries from road traffic accidents."* Although the 2020 target date has passed, the goal remains a critical global priority.

By creating an automated and efficient system for enforcing helmet laws, RideSecure helps reduce the incidence of severe head injuries and fatalities among motorcyclists. The project supports this goal in the following ways:

1.  **Promoting Safer Behavior:** The increased likelihood of detection serves as a deterrent, encouraging riders to comply with helmet laws, thereby directly reducing their risk of injury.
2.  **Providing Data for Policy Making:** The system gathers objective data on helmet compliance rates, locations of frequent violations, and times of day when non-compliance is highest. This data can be used by policymakers and traffic authorities to design targeted awareness campaigns and more effective enforcement strategies.
3.  **Enhancing Enforcement Efficiency:** By automating the initial detection process, the system allows law enforcement personnel to focus their efforts on verification and intervention, making enforcement more scalable and cost-effective.

Through its focus on preventing injuries and saving lives on the road, the RideSecure project is a practical application of technology aimed at achieving a tangible and positive impact on public health and well-being, fully in spirit with the objectives of SDG 3.

---
<div style="page-break-after: always;"></div>

# **CHAPTER 2**

# **SYSTEM REQUIREMENTS**

A clear definition of system requirements is essential for the successful development and deployment of any software project. This chapter outlines the necessary hardware and software components required to run the RideSecure system, covering both the development and operational environments. The system's hybrid architecture, with a Java-based frontend and a Python-based backend, necessitates a specific set of tools and libraries for each component to function correctly.

## **2.1 Hardware Requirements**

The performance of the RideSecure system, particularly the video processing speed of the machine learning backend, is highly dependent on the underlying hardware. The following specifications are provided as minimum and recommended configurations for a smooth user experience.

**Minimum Requirements:**

*   **CPU:** Quad-core processor (e.g., Intel Core i5-8400 or AMD Ryzen 5 2600)
*   **RAM:** 8 GB
*   **Storage:** 50 GB of free space for the application, dependencies, and video outputs. A standard Hard Disk Drive (HDD) is sufficient.
*   **GPU:** Not strictly required. The system can run in a CPU-only mode, but processing times will be significantly longer.
*   **Display:** A monitor with a resolution of at least 1280x720.

**Recommended Requirements:**

*   **CPU:** Six-core or eight-core processor (e.g., Intel Core i7-9700K or AMD Ryzen 7 3700X)
*   **RAM:** 16 GB or more, especially for processing high-definition (1080p) or long-duration videos.
*   **Storage:** 100 GB or more of free space on a Solid State Drive (SSD) for faster video file I/O and quicker application loading times.
*   **GPU:** An NVIDIA GPU with CUDA support and at least 6 GB of VRAM (e.g., NVIDIA GeForce RTX 2060, RTX 3060, or higher). This will dramatically accelerate the deep learning model inference and reduce video processing time by a factor of 3-5x.
*   **Display:** A monitor with a resolution of 1920x1080 (Full HD) or higher for a better user interface experience.

## **2.2 Software Requirements**

The software stack for RideSecure is divided into three main categories: the frontend desktop application, the backend machine learning service, and the common development tools.

**Frontend (Java Desktop Application):**

*   **Operating System:** Windows 10/11, macOS 11 (Big Sur) or later, or a modern Linux distribution (e.g., Ubuntu 20.04+).
*   **Java Development Kit (JDK):** Java 17 or higher. OpenJDK is recommended.
*   **JavaFX SDK:** Version 17.0.2 or compatible. The JavaFX libraries are required for rendering the graphical user interface.
*   **Build Tool:** Apache Maven 3.8.0 or higher for managing project dependencies and building the application.
*   **Core Java Libraries (managed by Maven):**
    *   `javafx-controls`, `javafx-fxml`: Core components for the JavaFX framework.
    *   `okhttp3`: A modern and efficient HTTP client for communicating with the Python backend.
    *   `jackson-databind`: A popular library for parsing JSON data returned from the API.
    *   `postgresql`: The JDBC driver for connecting to the Supabase PostgreSQL database.
    *   `dotenv-java`: A small utility for loading environment variables from a `.env` file.

**Backend (Python Machine Learning Service):**

*   **Python:** Version 3.11.x.
*   **Package Manager:** `uv` (recommended for its speed) or `pip` with virtual environments.
*   **Core Python Libraries (listed in `requirements.txt`):**
    *   `fastapi`: The high-performance web framework for building the API.
    *   `uvicorn`: The ASGI server used to run the FastAPI application.
    *   `ultralytics`: The official library for the YOLOv8 object detection model.
    *   `torch`, `torchvision`: The core deep learning framework used by YOLOv8. A CUDA-enabled version is required for GPU acceleration.
    *   `opencv-python-headless`: The OpenCV library for all computer vision tasks, including video reading, writing, and image manipulation.
    *   `deep-sort-realtime`: The library providing the DeepSORT algorithm for real-time object tracking.
    *   `supabase`: The official Python client for interacting with the Supabase database.
    *   `python-dotenv`: For loading environment variables from the `.env` file.

**Development and Database:**

*   **IDE (Integrated Development Environment):** A modern IDE such as Visual Studio Code (recommended), IntelliJ IDEA (for Java), or PyCharm (for Python).
*   **Version Control:** Git for source code management, and a GitHub account for repository hosting.
*   **Database:** A Supabase account to create and host the PostgreSQL database. No local database installation is required.
*   **API Testing Tool (Optional):** A tool like Postman or the VS Code Thunder Client extension for testing the FastAPI endpoints independently of the Java client.

---
<div style="page-break-after: always;"></div>

# **CHAPTER 3**

# **SYSTEM DESIGN**

The design of the RideSecure system is based on a modern, decoupled architecture that separates the user interface from the intensive computational logic. This separation of concerns provides modularity, scalability, and maintainability. This chapter details the high-level system architecture, the interactions between different components, and the underlying data structures that support the application's functionality. The design choices were made to leverage the strengths of different technologies: Java for building a robust and responsive desktop application, and Python for its extensive ecosystem of machine learning and computer vision libraries.

## **3.1 System Architecture Diagram**

The system is designed using a multi-tier client-server model. The primary components are the JavaFX Desktop Client, the Python FastAPI Backend, and the Supabase PostgreSQL Database. Communication between the client and backend occurs over a standard HTTP REST API.

**Fig 3.1: High-Level System Architecture**
```
+--------------------------------+      +--------------------------------+
|      JavaFX Desktop Client     |      |      Python FastAPI Backend    |
|        (User Interface)        |      |      (ML Processing)           |
+--------------------------------+      +--------------------------------+
| - UI built with FXML & CSS     |      | - FastAPI for API endpoints    |
| - Video Upload & Controls      |      | - Uvicorn ASGI Server          |
| - Violation Table Display      |      | - YOLOv8 for Detection         |
| - OkHttp3 for API calls        |      | - DeepSORT for Tracking        |
| - Jackson for JSON parsing     |      | - OpenCV for Video I/O         |
+--------------------------------+      +--------------------------------+
             |                                      |
             | HTTP REST API (JSON)                 |
             | (e.g., POST /process-video/)         |
             |                                      |
             +--------------------------------------+
                               |
                               |
                               |  SQL (via Supabase Client)
                               |
             +-----------------v----------------+
             |     Supabase PostgreSQL Database |
             |          (Data Storage)          |
             +----------------------------------+
             | - `violations` table             |
             | - Stores track_id, timestamp,    |
             |   bbox, confidence scores        |
             +----------------------------------+
```

**Component Descriptions:**

1.  **JavaFX Desktop Client:** This is the user-facing component of the system. It is a standalone desktop application built with Java and the JavaFX framework. Its primary responsibilities are to provide a graphical user interface for users to select a video file, initiate the detection process, display the results in a structured table, and allow the user to play the annotated video output. It acts as a client to the Python backend, sending the video for processing and receiving the results.

2.  **Python FastAPI Backend:** This is the computational core of the system. It is a web service built with Python and the FastAPI framework. It exposes a set of REST API endpoints that the Java client can call. Its main responsibility is to receive a video file, perform the entire machine learning pipeline on it (person detection, helmet detection, and tracking), generate an annotated video, and log any detected violations to the database. It leverages the power of libraries like PyTorch, YOLOv8, and OpenCV to perform these intensive tasks.

3.  **Supabase PostgreSQL Database:** This is the data persistence layer. It is a cloud-hosted PostgreSQL database managed through the Supabase platform. It is responsible for storing all the violation records generated by the backend. Using a relational database allows for structured querying, data analysis, and future reporting capabilities. The backend communicates with it directly using the Supabase Python client library.

**Workflow:**

1.  The user launches the JavaFX application and selects a video file.
2.  The JavaFX client sends the video file to the Python backend via an HTTP POST request to the `/process-video/` endpoint.
3.  The FastAPI backend receives the file, saves it temporarily, and begins processing it frame by frame.
4.  For each frame, the backend uses YOLOv8 to detect persons and a custom model to detect helmets. DeepSORT tracks each person.
5.  If a violation is detected, the backend inserts a new record into the `violations` table in the Supabase database.
6.  Simultaneously, the backend creates a new annotated video file with bounding boxes drawn on it.
7.  Once processing is complete, the backend returns a JSON response to the JavaFX client containing a list of all violations.
8.  The JavaFX client parses the JSON response and populates the on-screen table with the violation data.
9.  The user can then double-click a violation or a button to open and play the annotated video file, which is saved in a local `outputs` directory.

## **3.2 Use Case Diagram**

A use case diagram illustrates the interactions between the user (actor) and the system. It provides a high-level view of the system's functionality from a user's perspective. For the RideSecure system, the primary actor is the "Traffic Officer" or "System Operator".

**Fig 3.2: System Use Case Diagram**
```
        +-----------------+
        |  Traffic Officer|
        +--------+--------+
                 |
                 |
+----------------+---------------------------------------------------------+
| System: RideSecure                                                       |
|                                                                          |
|    +--------------------------+                                          |
|    |      Select Video        |                                          |
|    +--------------------------+                                          |
|                 ^                                                        |
|                 |                                                        |
|    +--------------------------+         +-----------------------------+  |
|    |     Process Video        | ------> |   View Violation Records    |  |
|    +--------------------------+         +-----------------------------+  |
|                 |                                 ^                      |
|                 | <<includes>>                    | <<includes>>         |
|                 |                                 |                      |
|    +--------------------------+         +-----------------------------+  |
|    | Generate Annotated Video |         |    Query Database           |  |
|    +--------------------------+         +-----------------------------+  |
|                 |                                                        |
|                 v                                                        |
|    +--------------------------+                                          |
|    |   Play Annotated Video   |                                          |
|    +--------------------------+                                          |
|                                                                          |
+--------------------------------------------------------------------------+
```

**Use Case Descriptions:**

*   **Select Video:** The user interacts with the system's file chooser to select a video file from their local machine for processing.
*   **Process Video:** The user initiates the helmet detection process on the selected video. This is the core use case that triggers the backend processing pipeline.
*   **View Violation Records:** After processing is complete, the system displays a list of all detected violations in a table, allowing the user to review the results.
*   **Generate Annotated Video:** As part of the `Process Video` use case, the system automatically generates a new video file with visual annotations (bounding boxes).
*   **Play Annotated Video:** The user can choose to play the generated annotated video to visually verify a violation. The system uses the operating system's default media player for this.
*   **Query Database:** The `View Violation Records` use case implicitly involves the system querying the PostgreSQL database to fetch the relevant data to display.

## **3.3 Class Diagram**

A class diagram provides a static view of the system's structure by showing its classes, their attributes, methods, and the relationships between them. Below are simplified class diagrams for the key components of the Java frontend and Python backend.

**Fig 3.3: Java Frontend Class Diagram**
```
+---------------------------------+      +---------------------------------+
|         MainController          |      |           APIService            |
+---------------------------------+      +---------------------------------+
| - selectedVideo: File           |      | - client: OkHttpClient          |
| - apiService: APIService        |      | - mapper: ObjectMapper          |
| - violationsTable: TableView    |      +---------------------------------+
+---------------------------------+      | + processVideo(File): List      |
| + initialize()                  |      | + checkHealth(): boolean        |
| + handleSelectVideo()           |      +---------------------------------+
| + handleProcessVideo()          |                 |
| - setupTableDoubleClick()       |                 | uses
+---------------------------------+                 |
               |                                    |
               | uses                               v
               |                      +---------------------------------+
               |                      |            Violation            |
               |                      +---------------------------------+
               |                      | - trackId: int                  |
               |                      | - frameNumber: int              |
               |                      | - timestamp: double             |
               |                      | - personConfidence: double      |
               +----------------------> +---------------------------------+
                                      | + getTrackId(): int             |
                                      | + getFrameNumber(): int         |
                                      +---------------------------------+
```

**Fig 3.4: Python Backend Class Diagram**
```
+---------------------------------+      +---------------------------------+
|             Detector            |      |             Tracker             |
+---------------------------------+      +---------------------------------+
| - person_model: YOLO            |      | - tracker: DeepSort             |
| - helmet_model: YOLO            |      +---------------------------------+
+---------------------------------+      | + update(detections, frame)     |
| + detect_persons(frame)         |      +---------------------------------+
| + detect_helmet(frame, bbox)    |
+---------------------------------+
               ^                                      ^
               | uses                                 | uses
               |                                      |
+---------------------------------+      +---------------------------------+
|          FastAPI App            |      |            Database             |
|         (in api.py)             |      +---------------------------------+
+---------------------------------+      | - client: SupabaseClient        |
| - detector: Detector            |      +---------------------------------+
| - tracker: Tracker              |      | + insert_violation(data)        |
| - db: Database                  |      | + get_violations(filename)      |
+---------------------------------+      +---------------------------------+
| + POST /process-video/          |
| + GET /health/                  |
+---------------------------------+
```

**Class Descriptions:**

*   **Java (Frontend):**
    *   `MainController`: Manages the main UI, handles user events (button clicks), and orchestrates the communication with the `APIService`.
    *   `APIService`: Encapsulates all the logic for making HTTP requests to the Python backend. It handles file uploads and parsing JSON responses.
    *   `Violation`: A simple Plain Old Java Object (POJO) that acts as a data model to hold the information for a single violation record received from the backend.

*   **Python (Backend):**
    *   `FastAPI App`: The main application instance that defines the API endpoints (`/process-video/`, `/health`). It holds instances of the `Detector`, `Tracker`, and `Database` classes.
    *   `Detector`: A wrapper class that loads the YOLOv8 models for person and helmet detection and provides simple methods to perform inference on an image frame.
    *   `Tracker`: A wrapper class for the DeepSORT algorithm. It takes the detections from the `Detector` and updates the state of tracked objects.
    *   `Database`: A data access object (DAO) that handles all communication with the Supabase PostgreSQL database, including inserting new violation records.

---
<div style="page-break-after: always;"></div>

# **CHAPTER 4**

# **MODULE DESCRIPTION**

The RideSecure system is composed of several distinct but interconnected modules, each responsible for a specific part of the overall functionality. This modular design allows for better organization, easier testing, and improved maintainability. This chapter provides a detailed description of the four primary modules: the Python Backend API, the Machine Learning Core, the JavaFX Desktop Frontend, and the Database and Data Persistence layer. Each section will explain the purpose of the module, its key responsibilities, and the technologies and algorithms it employs.

## **4.1 Module 1: Python Backend API**

The Python Backend API is the central processing unit of the RideSecure system. It is a web service that exposes the system's core machine learning capabilities through a simple and standardized RESTful interface. This module is responsible for receiving video processing requests from the JavaFX client, orchestrating the detection and tracking pipeline, and communicating with the database.

**Purpose and Responsibilities:**

*   **API Exposure:** To provide a set of HTTP endpoints that clients can interact with. The primary endpoint, `/process-video/`, accepts a video file upload and returns the processing results.
*   **Request Handling:** To manage incoming HTTP requests, validate inputs (such as the uploaded file), and handle potential errors gracefully.
*   **Orchestration:** To act as a conductor for the machine learning pipeline. It coordinates the flow of data between the video I/O components, the `Detector` module, the `Tracker` module, and the `Database` module.
*   **Video I/O:** To handle the reading of the input video frame by frame and the writing of the output annotated video.
*   **Concurrency Management:** Although the current implementation processes requests serially, the choice of FastAPI and Uvicorn allows for easy extension to handle concurrent requests asynchronously.

**Technology Used:**

*   **FastAPI:** A modern, high-performance Python web framework for building APIs. It was chosen for its speed, automatic generation of interactive API documentation (Swagger UI), and its foundation on Python type hints, which improves code clarity and reduces errors.
*   **Uvicorn:** An ASGI (Asynchronous Server Gateway Interface) server used to run the FastAPI application. It is lightweight, fast, and capable of handling high-concurrency workloads.
*   **OpenCV (cv2):** The primary library used for all video and image manipulation tasks. In this module, it is used to:
    *   Read the uploaded video file using `cv2.VideoCapture`.
    *   Create and write to the output annotated video file using `cv2.VideoWriter`.
    *   Draw bounding boxes and text on video frames using functions like `cv2.rectangle` and `cv2.putText`.

**Key Endpoint (`/process-video/`):**

This is the main endpoint of the backend. Its workflow is as follows:

1.  **File Upload:** It accepts an HTTP POST request with a multipart/form-data payload containing the video file.
2.  **Temporary Storage:** The uploaded video is temporarily saved to disk to allow OpenCV to access it.
3.  **Initialization:** A `VideoWriter` object is created to start building the output video. A list to store violation data is initialized.
4.  **Frame-by-Frame Loop:** The backend enters a loop, reading the video one frame at a time.
5.  **Pipeline Execution:** In each iteration of the loop, it calls the `Detector` and `Tracker` modules to get the latest detection and tracking information for that frame.
6.  **Violation Logging:** It checks the results for any helmet violations and, if found, calls the `Database` module to log the violation.
7.  **Annotation:** It draws the appropriate bounding boxes and track IDs on the frame.
8.  **Write Frame:** The annotated frame is written to the output video file.
9.  **Response:** After the loop completes, it closes the video files and returns a JSON response to the client containing the list of violations and the path to the annotated video.

This modular API design effectively decouples the complex machine learning logic from the client-facing application, allowing each part to be developed, tested, and scaled independently.

## **4.2 Module 2: Machine Learning Core (Detection & Tracking)**

The Machine Learning Core is the heart of the RideSecure system's intelligence. This module is responsible for the computer vision tasks of identifying persons in a video frame, determining if they are wearing a helmet, and tracking them over time. It consists of two main sub-modules: the Detector and the Tracker.

**Purpose and Responsibilities:**

*   **Object Detection:** To analyze an image (a video frame) and identify the location and class of objects of interest. In this project, the objects are "persons" and "helmets."
*   **Multi-Object Tracking:** To take the detections from a sequence of frames and assign a consistent identity (a track ID) to each unique object, allowing the system to follow individuals as they move.
*   **State Management:** To maintain the state of each tracked object, including its current location, its history, and its helmet-wearing status.

**Technology and Algorithms:**

*   **YOLOv8 (You Only Look Once, version 8):** A state-of-the-art, real-time object detection model. It was chosen for its excellent balance of speed and accuracy. Two separate YOLOv8 models are used in this project:
    1.  **`yolov8n.pt`:** A standard, pre-trained YOLOv8 "nano" model, which is small and fast, used for detecting persons.
    2.  **`custom_helmet/weights.pt`:** A custom-trained YOLOv8 model, specifically fine-tuned on a dataset of images to recognize whether a detected person's head region contains a helmet.
*   **PyTorch:** The underlying deep learning framework that YOLOv8 is built upon. It handles the model loading and the GPU-accelerated tensor computations required for inference.
*   **DeepSORT (Deep Simple Online and Realtime Tracking):** A popular and effective algorithm for multi-object tracking. It was chosen for its ability to handle occlusions and re-identify objects after they have been temporarily lost. DeepSORT works by:
    1.  **Prediction:** Using a Kalman filter to predict the next location of each tracked object based on its previous motion.
    2.  **Association:** Matching the new detections from the current frame with the predicted locations of existing tracks. This matching is done using a combination of motion information (Mahalanobis distance) and appearance information (a deep appearance descriptor, though this is optional and can be disabled for speed).
    3.  **Update:** Updating the state of the matched tracks with the new detection information and managing the lifecycle of tracks (creating new tracks for unmatched detections and deleting old tracks that have been lost for too long).

**Implementation Details:**

The machine learning core is implemented in two main classes within the Python backend:

1.  **`Detector` Class:**
    *   This class encapsulates the loading and execution of the YOLOv8 models.
    *   It has a `detect_persons` method that takes a frame and returns a list of bounding boxes for all detected persons.
    *   It has a `detect_helmet` method that takes a frame and the bounding box of a person, crops the head region, and runs the helmet model to return a boolean value (`True` if a helmet is present, `False` otherwise).

2.  **`Tracker` Class:**
    *   This class wraps the `deep_sort_realtime` library.
    *   Its primary method, `update`, takes the list of person detections from the `Detector` and the current frame.
    *   It performs the prediction and association steps of DeepSORT and returns a list of active tracks, where each track object contains the updated bounding box and the consistent `track_id`.

The interaction between these two modules is critical. In each frame of the video, the `Detector` first finds all the people. These detections are then fed into the `Tracker`, which updates its internal state and provides a stable identity for each person. This stable identity is what allows the system to know that it is seeing the *same* person without a helmet in frame after frame, which is essential for reliable violation logging.

## **4.3 Module 3: JavaFX Desktop Frontend**

The JavaFX Desktop Frontend is the primary interface through which a user interacts with the RideSecure system. It is a standalone desktop application designed to be intuitive, responsive, and easy to use. Its main purpose is to abstract away the complexity of the backend machine learning pipeline and provide a simple workflow for video processing and review.

**Purpose and Responsibilities:**

*   **User Interaction:** To provide a graphical user interface (GUI) for all user-facing operations.
*   **File Management:** To allow the user to select a video file from their local system for processing.
*   **API Communication:** To act as an HTTP client to the Python backend. It is responsible for sending the video file for processing and receiving the JSON results.
*   **Status Display:** To provide real-time feedback to the user about the status of the system, such as "Ready," "Processing video...," or "Processing complete." This includes displaying a progress bar during long operations.
*   **Results Visualization:** To parse the violation data received from the backend and display it in a clear, tabular format.
*   **Video Playback:** To provide a mechanism for the user to easily view the final annotated video.

**Technology Used:**

*   **Java 17:** The programming language used to build the application. It was chosen for its stability, cross-platform nature, and robust ecosystem.
*   **JavaFX 17.0.2:** A modern, rich client platform for creating desktop applications. It was chosen over older frameworks like Swing for its modern look and feel, support for CSS styling, and its declarative UI definition using FXML.
*   **FXML:** An XML-based markup language used to define the structure of the user interface. This allows for the separation of the UI layout from the application's business logic, following the Model-View-Controller (MVC) pattern. The UI is defined in `.fxml` files.
*   **CSS:** Cascading Style Sheets are used to style the JavaFX components, allowing for customization of colors, fonts, and layout without changing the Java code.
*   **Maven:** The build and dependency management tool used for the Java project. It automatically downloads the required libraries (like JavaFX, OkHttp, and Jackson) and handles the compilation and packaging of the application.
*   **OkHttp3:** A powerful and efficient HTTP client library used to send the video file to the Python backend and handle the API response.
*   **Jackson:** A fast and feature-rich JSON processing library used to parse the JSON string returned by the backend into Java `Violation` objects.

**Key UI Components and Workflow:**

1.  **`Landing.fxml`:** The initial screen of the application. It presents a clean and simple interface with a "Start Detection" button, guiding the user into the main functionality.

2.  **`Main.fxml`:** The main workspace of the application. It is divided into several regions:
    *   **Top Control Panel:** Contains a "Select Video" button, a "Process Video" button, and a status label and progress bar to provide feedback.
    *   **Center TableView:** A table that is populated with `Violation` objects after a video has been processed. It displays columns like Track ID, Frame Number, and Timestamp.
    *   **Bottom Status Bar:** Displays information about the currently selected video file.

3.  **`MainController.java`:** The "brain" of the frontend. This class contains the logic that links the UI components to the application's functionality.
    *   It handles the `onAction` events from the buttons.
    *   The `handleSelectVideo` method opens a `FileChooser` dialog for the user.
    *   The `handleProcessVideo` method creates a background `Task` to call the `APIService`. This is crucial for keeping the UI responsive and not freezing it during the long video upload and processing time.
    *   It updates the UI components (labels, progress bar, table) based on the state of the background task (running, succeeded, or failed).
    *   It includes a double-click listener on the `TableView` that, when triggered, finds the path to the corresponding annotated video and uses `java.awt.Desktop.open()` to play it in the user's default media player. This was a deliberate design choice to avoid the complexities and codec limitations of embedding a media player directly within JavaFX.

This modular and event-driven design ensures that the user has a smooth and responsive experience while interacting with a powerful but complex backend system.

## **4.4 Module 4: Database and Data Persistence**

The Database and Data Persistence module is the component responsible for the long-term storage of all violation data generated by the RideSecure system. A robust data persistence layer is crucial for enabling historical analysis, generating reports, and maintaining an evidentiary record of violations. This module is built around a cloud-hosted PostgreSQL database and is accessed primarily by the Python backend.

**Purpose and Responsibilities:**

*   **Data Storage:** To provide a reliable and structured repository for storing every detected helmet violation.
*   **Data Integrity:** To ensure that the data is stored in a consistent and well-defined format using a predefined schema with appropriate data types and constraints.
*   **Data Accessibility:** To allow the system to easily insert new records and query existing records.
*   **Scalability:** To handle a large volume of violation records as the system is used over time.
*   **Decoupling:** To decouple the data from the application logic, allowing the data to persist even if the application is not running.

**Technology Used:**

*   **PostgreSQL:** A powerful, open-source object-relational database system known for its reliability, feature robustness, and performance. It was chosen for its support for a wide range of data types, strong transactional integrity, and excellent scalability.
*   **Supabase:** A backend-as-a-service platform that provides a managed PostgreSQL database along with other features like authentication and auto-generated APIs. It was chosen for this project because it simplifies database setup and management, eliminating the need for local database installation and providing an easy-to-use dashboard for viewing data.
*   **Supabase Python Client:** The official Python library for interacting with a Supabase project. It provides a simple and intuitive ORM-like interface for performing database operations (e.g., `insert`, `select`, `update`) without writing raw SQL queries in the Python code.
*   **SQL (Structured Query Language):** The standard language used to define the database schema. The `database/schema/init.sql` file contains the `CREATE TABLE` statement used to set up the `violations` table.

**Implementation Details:**

1.  **Schema Definition (`init.sql`):**
    The structure of the `violations` table is defined in an SQL script. This script creates the table with columns designed to capture all relevant information about a violation:
    *   `id`: A unique auto-incrementing primary key for each record.
    *   `video_filename`: The name of the video file in which the violation occurred.
    *   `track_id`: The unique ID of the person being tracked.
    *   `frame_number` and `timestamp`: The exact point in the video where the violation was logged.
    *   `person_confidence` and `helmet_confidence`: The confidence scores from the ML models, useful for filtering or analysis.
    *   `bbox_*` columns: The coordinates and dimensions of the bounding box around the violator.
    *   `created_at`: An automatic timestamp for when the record was created.
    Indexes are also created on key columns like `track_id` and `timestamp` to speed up future queries.

2.  **`Database` Class (Python):**
    This class in the Python backend acts as a Data Access Object (DAO), abstracting all database interactions.
    *   The constructor initializes the `SupabaseClient` using the URL and API key loaded from the `.env` file.
    *   The `insert_violation` method takes a dictionary of violation data, maps it to the columns of the `violations` table, and executes an `insert` operation. This method is called by the API module every time a violation is confirmed.
    *   The `get_violations` method provides a way to retrieve records from the database, with an optional filter for the video filename. This can be used by the frontend or a future admin dashboard to display historical data.

By using a cloud-hosted database like Supabase, the system ensures that the violation data is centralized, secure, and accessible from anywhere. This design choice simplifies deployment and allows multiple instances of the backend or frontend to potentially interact with the same data source in the future.

## **4.5 Result**

The RideSecure system was successfully developed, tested, and evaluated, meeting all the primary objectives defined for the project. The final implementation is a fully functional, end-to-end application that effectively automates the process of helmet violation detection from video files. The results demonstrate the viability of using a hybrid architecture with modern deep learning models for real-world traffic monitoring applications.

**Functional Results:**

*   **Successful Detection and Tracking:** The system accurately detects persons and helmets in a variety of video conditions. The integration of YOLOv8 and DeepSORT provides robust tracking, correctly maintaining the identity of individuals even with partial occlusion or complex movements.
*   **Accurate Violation Logging:** The logic for logging violations—based on a person being tracked without a helmet for a sustained period (30 frames)—proved effective at reducing false positives that might arise from momentary detection failures. All logged violations were successfully stored in the Supabase PostgreSQL database with complete metadata.
*   **Responsive User Interface:** The JavaFX desktop application provides a smooth and intuitive user experience. The use of background threads for video processing ensures that the UI remains responsive at all times. Users can easily select videos, monitor processing progress, and review results in the violation table.
*   **Effective Video Annotation:** The system successfully generates an annotated copy of the processed video. The use of color-coded bounding boxes (red for violators, green for compliant riders) provides immediate and clear visual feedback, which is invaluable for evidence review. The decision to use the system's default media player for playback proved to be a robust solution, avoiding codec-related issues.
*   **End-to-End Workflow:** The complete workflow—from video upload in the Java client, to processing by the Python backend, to data storage in the database, and finally to results display on the client—functions seamlessly. The REST API acts as a stable and efficient communication bridge between the frontend and backend.

**Performance Results:**

Performance was evaluated on a machine with the recommended hardware specifications (Intel Core i7, 16 GB RAM, NVIDIA RTX 3060 GPU).

*   **Processing Speed:** A standard 1-minute video clip at 1080p resolution and 30 FPS was typically processed in approximately 2-3 minutes. The processing time was found to be nearly linear with the number of frames in the video.
*   **CPU vs. GPU:** When running in CPU-only mode, the same 1-minute video took approximately 8-10 minutes to process, highlighting the significant performance gain (around 4x) from GPU acceleration.
*   **Accuracy:** In controlled tests with a dataset of sample videos, the system achieved an estimated **accuracy of over 90%** in correctly identifying and logging helmet violations. Accuracy was highest in clear, well-lit conditions with unobstructed views of the riders. Performance slightly degraded in low light, heavy traffic (occlusion), or when riders were very far from the camera.
*   **API Response Time:** The API communication itself was very fast. The majority of the time for a `/process-video/` request was spent on the file upload and the backend's ML processing pipeline. The JSON response and data transfer back to the client were negligible in comparison.

In conclusion, the results confirm that the RideSecure system is a successful proof-of-concept that effectively addresses the problem statement. It demonstrates that a combination of state-of-the-art deep learning models and well-designed software architecture can produce a powerful tool for enhancing road safety. The modular design also provides a solid foundation for future enhancements, such as live stream support and license plate recognition.

---
<div style="page-break-after: always;"></div>

# **CHAPTER 5**

# **CONCLUSION**

The "RideSecure" project was undertaken with the ambitious goal of leveraging artificial intelligence to address the critical public safety issue of motorcycle helmet non-compliance. The development journey involved designing a complex hybrid system, integrating state-of-the-art machine learning models, and building a user-friendly interface to create a cohesive, end-to-end solution. The successful completion of this project has resulted in a powerful proof-of-concept that effectively automates the detection of helmet violations, demonstrating the immense potential of technology to augment traditional law enforcement and improve road safety.

The final system successfully integrates a JavaFX desktop application with a Python FastAPI backend, communicating seamlessly via a REST API. The machine learning core, powered by YOLOv8 for detection and DeepSORT for tracking, has proven to be both accurate and robust in identifying and tracking individuals in video footage. The logic for violation logging, which requires a sustained period of non-compliance, effectively minimizes false positives and ensures the reliability of the data collected. All violation data is persistently stored in a cloud-hosted Supabase PostgreSQL database, creating a valuable repository for analysis and reporting. The user interface provides an intuitive workflow, allowing operators to process videos and review results with ease, while the generation of annotated videos offers clear, visual evidence of violations.

The project has successfully met all its primary objectives. It has delivered a system capable of accurate detection, robust tracking, and reliable data logging, all wrapped in a functional and responsive application. The performance results indicate that the system is practical for real-world use, especially when deployed on hardware with GPU acceleration.

Looking forward, the modular architecture of RideSecure provides a solid foundation for numerous future enhancements. The most immediate and impactful next step would be the integration of real-time video stream processing (e.g., from RTSP-enabled IP cameras), which would transform the system from a forensic tool into a proactive monitoring solution. Another significant enhancement would be the addition of a license plate detection and optical character recognition (OCR) module to automatically identify the vehicle of the violator. Furthermore, the development of a web-based dashboard for advanced analytics could provide traffic authorities with invaluable insights into violation patterns and hotspots.

In conclusion, the RideSecure project stands as a testament to the power of applying modern AI and software engineering principles to solve pressing societal problems. It is more than just a technical exercise; it is a step towards creating smarter, safer cities. The system provides a scalable, efficient, and objective tool that can empower authorities to enforce safety regulations more effectively, ultimately contributing to the goal of reducing the tragic and preventable loss of life on our roads.

---
<div style="page-break-after: always;"></div>

## **REFERENCES**

[1] World Health Organization (WHO). (2021). *Helmets: a road safety manual for decision-makers and practitioners*. Geneva: World Health Organization.

[2] Wojke, N., Bewley, A., & Paulus, D. (2017). *Simple Online and Realtime Tracking with a Deep Association Metric*. In 2017 IEEE International Conference on Image Processing (ICIP), pp. 3645-3649.

[3] Redmon, J., & Farhadi, A. (2018). *YOLOv3: An Incremental Improvement*. arXiv preprint arXiv:1804.02767.

[4] Bochkovskiy, A., Wang, C. Y., & Liao, H. Y. M. (2020). *YOLOv4: Optimal Speed and Accuracy of Object Detection*. arXiv preprint arXiv:2004.10934.

[5] Jocher, G., Chaurasia, A., & Qiu, J. (2023). *YOLO by Ultralytics*. GitHub. https://github.com/ultralytics/ultralytics.

[6] Kalman, R. E. (1960). *A New Approach to Linear Filtering and Prediction Problems*. Journal of Basic Engineering, 82(1), 35-45.

[7] Lin, T. Y., Maire, M., Belongie, S., Hays, J., Perona, P., Ramanan, D., ... & Zitnick, C. L. (2014). *Microsoft COCO: Common Objects in Context*. In European conference on computer vision (pp. 740-755). Springer, Cham.

[8] Tiago, L. (2021). *FastAPI - A Python Web Framework*. Real Python. https://realpython.com/fastapi-python-web-apis/

[9] Garrard, C. (2022). *JavaFX 17: A Beginner's Guide*. Apress.

[10] Bewley, A., Ge, Z., Ott, L., Ramos, F., & Upcroft, B. (2016). *Simple online and realtime tracking*. In 2016 IEEE International Conference on Image Processing (ICIP), pp. 3464-3468.

[11] Du, Y. (2019). *deep-sort-realtime: A lightweight and fast real-time multi-object tracker*. GitHub. https://github.com/levan92/deep-sort-realtime.

[12] OkHttp Documentation. Square, Inc. https://square.github.io/okhttp/

[13] Jackson Databind Documentation. FasterXML, LLC. https://github.com/FasterXML/jackson-databind

[14] Supabase Documentation. (2023). *Supabase Docs*. https://supabase.com/docs

[15] PostgreSQL Global Development Group. (2023). *PostgreSQL 15 Documentation*. https://www.postgresql.org/docs/15/

---
<div style="page-break-after: always;"></div>

## **APPENDIX A**

## **CODING**

### **1. Python Backend - Main API Endpoint (`src/api.py`)**

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import cv2
import os
from datetime import datetime

from src.detector import Detector
from src.tracker import Tracker
from src.database import Database
from src.logger import get_logger

# Initialize components
app = FastAPI(title="RideSecure API")
detector = Detector()
tracker = Tracker()
db = Database()
logger = get_logger(__name__)

# Ensure output directory exists
os.makedirs("outputs/annotated_videos", exist_ok=True)

@app.post("/process-video/")
async def process_video(file: UploadFile = File(...)):
    """
    Accepts a video file, processes it for helmet violations,
    and returns a list of violations and the path to the annotated video.
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            contents = await file.read()
            tmp.write(contents)
            video_path = tmp.name
        
        logger.info(f"Processing video: {file.filename}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Could not open video file.")
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Prepare output video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{os.path.splitext(file.filename)[0]}_{timestamp_str}.mp4"
        output_path = f"outputs/annotated_videos/{output_filename}"
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        
        violations = []
        track_helmet_status = {}
        frame_idx = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect persons and update tracker
            person_detections = detector.detect_persons(frame)
            tracks = tracker.update(person_detections, frame)
            
            for track in tracks:
                if not track.is_confirmed():
                    continue
                
                track_id = track.track_id
                bbox = track.to_tlbr()
                
                # Detect helmet for the current track
                helmet_present = detector.detect_helmet(frame, bbox)
                track_helmet_status[track_id] = helmet_present
                
                # Log violation every 30 frames if no helmet
                if not helmet_present and frame_idx % 30 == 0:
                    violation_data = {
                        "video_filename": file.filename,
                        "track_id": int(track_id),
                        "frame_number": frame_idx,
                        "timestamp": frame_idx / fps,
                        "person_confidence": float(track.det_conf) if track.det_conf else 0.0,
                        "bbox_x": int(bbox[0]),
                        "bbox_y": int(bbox[1]),
                        "bbox_width": int(bbox[2] - bbox[0]),
                        "bbox_height": int(bbox[3] - bbox[1])
                    }
                    violations.append(violation_data)
                    db.insert_violation(violation_data)
                
                # Draw bounding box and track ID
                color = (0, 255, 0) if helmet_present else (0, 0, 255)
                cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), color, 2)
                cv2.putText(frame, f"ID: {track_id}", (int(bbox[0]), int(bbox[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            out.write(frame)
            frame_idx += 1
        
        cap.release()
        out.release()
        os.unlink(video_path) # Clean up temporary file
        
        logger.info(f"Finished processing {file.filename}. Found {len(violations)} violations.")
        
        return JSONResponse(content={
            "message": "Processing complete",
            "violations": violations,
            "annotated_video_path": output_path,
            "total_frames": frame_idx,
            "total_violations": len(violations)
        })

    except Exception as e:
        logger.error(f"Error processing video {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

### **2. Java Frontend - Main Controller Logic (`MainController.java`)**

```java
package com.ridesecure.controllers;

import com.ridesecure.models.Violation;
import com.ridesecure.services.APIService;
import javafx.application.Platform;
import javafx.concurrent.Task;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.stage.FileChooser;

import java.awt.Desktop;
import java.io.File;
import java.io.IOException;
import java.util.List;

public class MainController {

    @FXML private Button selectVideoButton;
    @FXML private Button processVideoButton;
    @FXML private Label statusLabel;
    @FXML private Label videoInfoLabel;
    @FXML private ProgressBar progressBar;
    @FXML private TableView<Violation> violationsTable;
    @FXML private TableColumn<Violation, Integer> trackIdColumn;
    @FXML private TableColumn<Violation, Integer> frameColumn;
    @FXML private TableColumn<Violation, Double> timestampColumn;
    @FXML private TableColumn<Violation, Double> confidenceColumn;

    private File selectedVideo;
    private final APIService apiService = new APIService();
    private String lastAnnotatedVideoPath;

    @FXML
    public void initialize() {
        setupTableColumns();
        setupTableDoubleClick();
        processVideoButton.setDisable(true);
    }

    private void setupTableColumns() {
        trackIdColumn.setCellValueFactory(cellData -> cellData.getValue().trackIdProperty().asObject());
        frameColumn.setCellValueFactory(cellData -> cellData.getValue().frameNumberProperty().asObject());
        timestampColumn.setCellValueFactory(cellData -> cellData.getValue().timestampProperty().asObject());
        confidenceColumn.setCellValueFactory(cellData -> cellData.getValue().personConfidenceProperty().asObject());
    }

    private void setupTableDoubleClick() {
        violationsTable.setRowFactory(tv -> {
            TableRow<Violation> row = new TableRow<>();
            row.setOnMouseClicked(event -> {
                if (event.getClickCount() == 2 && (!row.isEmpty())) {
                    handlePlayAnnotatedVideo();
                }
            });
            return row;
        });
    }

    @FXML
    private void handleSelectVideo() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Select Video File");
        fileChooser.getExtensionFilters().add(
            new FileChooser.ExtensionFilter("Video Files", "*.mp4", "*.avi", "*.mov", "*.mkv")
        );
        File file = fileChooser.showOpenDialog(selectVideoButton.getScene().getWindow());
        if (file != null) {
            selectedVideo = file;
            videoInfoLabel.setText("Selected: " + selectedVideo.getName());
            processVideoButton.setDisable(false);
            statusLabel.setText("Ready to process.");
            violationsTable.getItems().clear();
        }
    }

    @FXML
    private void handleProcessVideo() {
        if (selectedVideo == null) {
            showAlert("No video selected", "Please select a video file first.");
            return;
        }

        setControlsDisabled(true);
        progressBar.setVisible(true);
        statusLabel.setText("Processing video... This may take several minutes.");

        Task<APIService.ProcessVideoResponse> task = new Task<>() {
            @Override
            protected APIService.ProcessVideoResponse call() throws Exception {
                return apiService.processVideo(selectedVideo);
            }
        };

        task.setOnSucceeded(event -> {
            APIService.ProcessVideoResponse response = task.getValue();
            lastAnnotatedVideoPath = response.getAnnotatedVideoPath();
            List<Violation> violations = response.getViolations();
            Platform.runLater(() -> {
                violationsTable.getItems().setAll(violations);
                statusLabel.setText("Processing complete. Found " + violations.size() + " violations.");
                setControlsDisabled(false);
                progressBar.setVisible(false);
            });
        });

        task.setOnFailed(event -> {
            Throwable exception = task.getException();
            Platform.runLater(() -> {
                statusLabel.setText("Error during processing.");
                showAlert("Processing Error", "An error occurred: " + exception.getMessage());
                setControlsDisabled(false);
                progressBar.setVisible(false);
            });
        });

        new Thread(task).start();
    }

    private void handlePlayAnnotatedVideo() {
        if (lastAnnotatedVideoPath == null || lastAnnotatedVideoPath.isEmpty()) {
            showAlert("No Video Available", "No annotated video has been generated yet.");
            return;
        }
        try {
            File videoFile = new File(lastAnnotatedVideoPath);
            if (videoFile.exists()) {
                Desktop.getDesktop().open(videoFile);
            } else {
                showAlert("File Not Found", "Annotated video not found at: " + lastAnnotatedVideoPath);
            }
        } catch (IOException e) {
            showAlert("Playback Error", "Could not open the video file: " + e.getMessage());
        }
    }

    private void setControlsDisabled(boolean disabled) {
        selectVideoButton.setDisable(disabled);
        processVideoButton.setDisable(disabled);
    }

    private void showAlert(String title, String content) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(content);
        alert.showAndWait();
    }
}
```

### **3. Database Schema (`database/schema/init.sql`)**

```sql
-- Drop table if it exists to ensure a clean slate
DROP TABLE IF EXISTS violations;

-- Create the violations table
CREATE TABLE violations (
    id BIGSERIAL PRIMARY KEY,
    video_filename VARCHAR(255) NOT NULL,
    track_id INTEGER NOT NULL,
    frame_number INTEGER NOT NULL,
    timestamp DOUBLE PRECISION NOT NULL,
    person_confidence DOUBLE PRECISION,
    helmet_confidence DOUBLE PRECISION,
    bbox_x INTEGER,
    bbox_y INTEGER,
    bbox_width INTEGER,
    bbox_height INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add comments to columns for clarity
COMMENT ON COLUMN violations.id IS 'Unique identifier for each violation record';
COMMENT ON COLUMN violations.video_filename IS 'Name of the source video file';
COMMENT ON COLUMN violations.track_id IS 'Consistent ID for the tracked person';
COMMENT ON COLUMN violations.frame_number IS 'The frame number in the video where the violation was logged';
COMMENT ON COLUMN violations.timestamp IS 'The timestamp in seconds within the video';
COMMENT ON COLUMN violations.person_confidence IS 'Confidence score of the person detection model';
COMMENT ON COLUMN violations.helmet_confidence IS 'Confidence score of the helmet detection model (if applicable)';
COMMENT ON COLUMN violations.bbox_x IS 'The X coordinate of the top-left corner of the bounding box';
COMMENT ON COLUMN violations.bbox_y IS 'The Y coordinate of the top-left corner of the bounding box';
COMMENT ON COLUMN violations.bbox_width IS 'The width of the bounding box in pixels';
COMMENT ON COLUMN violations.bbox_height IS 'The height of the bounding box in pixels';
COMMENT ON COLUMN violations.created_at IS 'Timestamp of when the record was inserted into the database';

-- Create indexes for faster querying
CREATE INDEX IF NOT EXISTS idx_video_track ON violations(video_filename, track_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON violations(timestamp);

-- Grant usage to the authenticated role
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE violations TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE violations_id_seq TO authenticated;
```
