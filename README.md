# The Recruiter

> Tugas Besar 3 - IF2211 Strategi Algoritma 2025
<p align="center">
    <img src="https://github.com/user-attachments/assets/7b2a1bda-2355-42bf-9967-07e4b19936a0">
</p>
    <h3 align="center">The Recruiter</h3>
<p align="center">
    Leave your moral and ethics, let a rational computer decision scan your applicant's CV
    <br />
    <br />
    <a href="https://github.com/l0stplains/Tubes3_TheRecruiter/releases/">Releases</a>
    ·
    <a href="./docs/">Project Report & Specification (Bahasa Indonesia)</a>
</p>

## Table of Contents <a name="table-of-contents"></a>

- [The Team](#team)
- [About](#about)
- [Algorithms](#algorithms)
- [How to Run](#how-to-run)

---

## The Team <a name="team"></a>
<div align="right">(<a href="#table-of-contents">back to top</a>)</div> 

<table>
       <tr align="left">
         <td><b>NIM</b></td>
         <td><b>Name</b></td>
         <td align="center"><b>GitHub</b></td>
       </tr>
       <tr align="left">
         <td>13523002</td>
         <td>Refki Alfarizi</td>
         <td align="center" >
           <div style="margin-right: 20px;">
           <a href="https://github.com/l0stplains" ><img src="https://avatars.githubusercontent.com/u/78079998?v=4" width="48px;" alt=""/> <br/> <sub><b> @l0stplains </b></sub></a><br/>
           </div>
         </td>
       </tr>
       <tr align="left">
         <td>13523085</td>
         <td>Muhammad Jibril Ibrahim</td>
         <td align="center" >
           <div style="margin-right: 20px;">
           <a href="https://github.com/BoredAngel" ><img src="https://avatars.githubusercontent.com/u/168176400?v=4" width="48px;" alt=""/> <br/> <sub><b> @BoredAngel </b></sub></a><br/>
           </div>
         </td>
       </tr>
         <tr align="left">
         <td>13523090</td>
         <td>Nayaka Ghana Subrata</td>
         <td align="center" >
           <div style="margin-right: 20px;">
           <a href="https://github.com/Nayekah" ><img src="https://avatars.githubusercontent.com/u/138268904?v=4" width="48px;" alt=""/> <br/> <sub><b> @Nayekah </b></sub></a><br/>
           </div>
         </td>
       </tr>
</table>

---

## About <a name="about"></a>
<div align="right">(<a href="#table-of-contents">back to top</a>)</div>  

<p align="justify">This project is the third and last milestone project of 2025 IF2211 Algorithm Strategy course at <a href="https://itb.ac.id" target="_blank">Institut Teknologi Bandung</a>.</p>

<p align="justify">This project implements a simplified Applicant Tracking System (ATS) designed to extract and analyze digital CVs using pattern matching techniques. The system processes PDF documents by converting them into plain text, then searches for user-specified keywords using the Knuth-Morris-Pratt, Boyer-Moore, or Aho-Corasick string matching algorithm. If no exact matches are found, the system performs fuzzy matching based on Levenshtein Distance, with a configurable similarity threshold. It also extract applicants data summary using RegEx. </p>

---

## Algorithms <a name="algorithms"></a>
<div align="right">(<a href="#table-of-contents">back to top</a>)</div>  

--- 

## How to Run <a name="how-to-run"></a>

<div align="right">(<a href="#table-of-contents">back to top</a>)</div>  

### Requirements
- Python 3.8
- Docker
- Dependencies (listed [here](./pyproject.toml))

> [!IMPORTANT]
> This project is managed with [uv](https://github.com/astral-sh/uv) and it's recommended to install the package manager on your system and run this application (_not glazing btw_)

### Running the Application With `uv`
1. Clone this repo
   ```bash
   git clone https://github.com/l0stplains/Tubes3_TheRecruiter.git
   ```
   > or just clicks button on your git gui if you feel uncomfortable with terminal
2. Navigate to the cloned repository.
   ```bash
   cd ./Tubes3_TheRecruiter
   ```
3. Setup `.env` like [example](./.env.example) with your data
   ```dotenv
   # Database Configuration
    DB_HOST=localhost
    DB_PORT=2025
    DB_NAME=ats_system
    DB_USER=gongyoo
    DB_PASSWORD=REDACTED
    
    # MySQL Root
    MYSQL_ROOT_PASSWORD=REDACTED
    
    # Encryption Configuration
    ENCRYPTION_PASSWORD=REDACTED
   ```
4. Run `docker-compose` (make sure you have docker instance running)
   ```bash
   docker-compose up -d
   ```
5. Make sure to use python 3.8:
   ```bash
   uv python install 3.8
   uv python pin 3.8
   ```
6. Setup OS-specific library
    - **Windows**
      ```bash
      pip install PyQtWebEngine
      ```
    - **Linux**
      ```bash
      uv add PyQtWebEngine
      ```
    <details>
        <summary>
            <i>Why Windows can't use <code>uv</code>?</i>
        </summary>
        <br/>
        The short answer is that <b>it's not compatible</b>. <i>well at least for this project</i>
        <br/>
        <br/>
        Using <code>uv</code> means we need to use a specific version constraints of the library that <b>built for</b> the project python version (3.8). The problem is that PyQtWebEngine version for python 3.8 does not support windows. By using pip install directly it bypass the constraints and install it for the system or venv. 
    </details>
7. Place all the CV pdf in `data/` folder at root
8. Run the seeder to fill the database
   ```bash
   uv run scripts/seeder.py
   ```
9. Run the program:
   ```bash
   uv run -m src -d gui
   ```
> [!NOTE]
> If you are planning to develop, you must set your system python to use version 3.8 and install pyqt5-tools

---
