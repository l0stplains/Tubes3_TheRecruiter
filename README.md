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

## How to Run <a name="how-to-run"></a>

<div align="right">(<a href="#table-of-contents">back to top</a>)</div>  

### Requirements
- Python 3.8
- Dependencies (listed [here](./pyproject.toml))

> [!IMPORTANT]
> This project is managed with [uv](https://github.com/astral-sh/uv) and it's recommended to install the package manager on your system and run this application (not glazing btw)

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
3. Make sure to use python 3.8:
   ```bash
   uv python install 3.8
   uv python pin 3.8
   ```
4. Run the program:
   ```bash
   uv run -m src
   ```
> [!NOTE]
> If you are planning to develop, you must set your system python to use version 3.8 and install pyqt5-tools

### Running the Application With `pip` (not recommended)
1. Clone this repo
   ```bash
   git clone https://github.com/l0stplains/Tubes3_TheRecruiter.git
   ```
   > or just clicks button on your git gui if you feel uncomfortable with terminal
2. Navigate to the cloned repository.
      ```bash
   cd ./Tubes3_TheRecruiter
   ```
3. Make sure to use python 3.8
4. Install all dependencies listed on the [pyproject.toml](./pyproject.toml) file
5. Run the program:
   ```bash
   python -m src
   ```
---
