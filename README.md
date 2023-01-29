# Investment Advisor

### The Investment Advisor application will assess an investor's risk tolerance and his/her's capacity to absorbe risk. Based on those evaluations, two corresponding risk scores will be calculated and associated investment portfolios will be chosen from our ETFs offering. Their performance will be assessed and compared to the Benchmark portfolio of 40% Bonds 60% Stock. To increase clients' awareness of our new Digital Assets enhanced portfolio, we will include the comparison performance of this fund too.

---

![ETF](Images/Inv_advice.png)

---

## Table of contents

1. [Technologies](#technologies)
2. [Installation Guide](#installation-guide)
3. [Usage](#usage)
4. [Contributors](#contributors)
5. [License](#license)

---

## Technologies

`Python 3.9`

`Jupyter lab`

_Prerequisites_

1. `Pandas` is a Python package that provides fast, flexible, and expressive data structures designed to make working with large sets of data easy and intuitive.

   - [pandas](https://github.com/pandas-dev/pandas) - for the documentation, installation guide and dependencies.

2. `PyViz` is a Python visualization package that provides a single platform for accessing multiple visualization libraries. One of these libraries is hvPlot. <br/>

   - [PyViz ](https://pyviz.org/) - for guidance on how to start visualization, interactive visualization, styles and layouts customazation.
   - [hvPlot ](https://hvplot.holoviz.org/) is a visualization library that is designed to work with Pandas DataFrames and that we can use to create interactive plots for our data.<br/>

3. `SQLAlchemy` is an open-source SQL library for Python. It is designed to ease the communication between Python-based programs and databases"

   - [SQLAlchemy ](https://www.sqlalchemy.org/) - for information on the library, its features and installation instructions.<br/>

4. `Voilà` builds interactive web applications directly from our Jupyter notebooks.

   - [Voilà ](https://voila.readthedocs.io/en/stable/) - to read more about deploying, installing and customizing<br/>

---

## Installation Guide

Jupyter lab is a preferred software to work with Risk Return Analysis application.<br/> Jupyter lab is a part of the **[anaconda](https://www.anaconda.com/)** distribution package and therefore it is recommended to download **anaconda** first.<br/> Once dowloaded, run the following command in your terminal to lauch Jupyter lab:

```python
jupyter lab
```

Before using the application first install the following dependencies by using your terminal:

To install pandas run:

```python
#  PuPi
pip install pandas
```

```python
# or conda
conda install pandas
```

To install PyViz, in Terminal run:

```python
# conda
conda install -c pyviz hvplot geoviews
```

Confirm the installation of all the PyViz packages by running the following commands in Terminal type:

```python
 conda list hvplot
```

To install SQLAlchemy, in Terminal run:

```python
# PuPi
pip install SQLAlchemy
```

Confirm the installation of the SQLAlchemy package by running the following commands in Terminal type:

```python
 conda list sqlalchemy
```

To install Voilà, in Terminal run:

```python
# PuPi
pip install voila
```

Confirm the installation of the Voilà package by running the following commands in Terminal type:

```python
 conda list voila
```

---

## Usage

> Application summary<br/>

Investment Advisor assists ......<br/>
Furthermore, Streamlit library transforms Investment Advisor into an interactive web application that nontechnical users without any coding experience can use.

- The analyzis begings by informing the users about the portfolio of stocks that form the ETF:<br/>
  ![ETF_table](Images/ETF_table.PNG)<br/>
- Next, a single stock's daily returns and cumulative returns are displayed and the trends are analyzed:<br/>
  ![ETF_returns](Images/PYPL_returns.png)<br/>
  ![ETF_c_returns](Images/PYPL_C_returns.png)<br/>
- A zoom into top 10 PPYL's returns and the information on when the stock was traded above $200 is also provided:<br/>
  ![ETF_top](Images/PYPL_highest.PNG)<br/>
  ![ETF_200](Images/PPYL_200.PNG)<br/>
- We procede wtih the ETF's cumulative returns analyzis:<br/>
  ![ETF_returns](Images/ETF_returns.png)<br/>
- We finalyze with performance comparison between the sinle stock (PYPL) and the ETF:<br/>
  ![ETF_PPYL](Images/ETF_PPYL.png)<br/>
- Voilà library is deployed to give web based interactive experience to the tool's users:<br/>
  ![Voila](Images/voila.PNG)<br/>

  `Play Streamlit demo to use the application`<br/>

<video src=ETF_Analyzer.mp4 controls="controls" style="max-width: 730px;"></video>

> Getting started<br/>

- To use ETF Analyzer first clone the repository to your PC.<br/>
- Open `Jupyter lab` as per the instructions in the [Installation Guide](#installation-guide) to run the application.<br/>

- Run Voilà in the Terminal: Voilà accepts a path to the notebook and then generates a web app with any visualizations or output that were generated in the Jupyter notebook. The code is simple:

```python
voila <relative-path-to-notebook>
```

---

## Contributors

Contact Details:

Boris Dudkin:

- [Email](boris.dudkin@gmail.com)
- [LinkedIn](www.linkedin.com/in/Boris-Dudkin)

Add yours

---

## License

MIT

---
