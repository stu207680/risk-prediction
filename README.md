# The way to success! - Or in other words: README!

## Each story has a beginning...
Dear reader, if you read this I'm probably go... - Wait a moment! Wrong text file! Which file is this? - Ah, a readme file! But for what?!  
*background noise:* ***CO2-efficient ship routing*** *project!!*  
Ah, I remember! It's for my Master thesis. I'm such a smart boi! :boy:  
*background noise (again):* ***CO2-efficient ship routing*** *project!!!!*  
Okay, okay! I get it! Such a rude background noise! Nevertheless, let's write a helpful readme file!  
For those who don't know me: My name is Mr. **Me**, first name **Read** and I will guide you through time and... - Stop! Again, wrong setting! Soooo, where I was? - Ah! I wanted to say that I will guide you through all steps to use this framework.

## Chapter I-I: The awakening!
Soooo, to use this framework you will need only two things (and several other things):
 - either a [Mac or PC](https://images.iskysoft.com/images/blog/12.jpg?_gl=1*1axm8jd*_ga*MTQzMzQ5NTQ0NC4xNjUyOTY0Nzkz*_ga_24WTSJBD5B*MTY1Mjk2NDc5My4xLjEuMTY1Mjk2NDgwNS40OA..), and
 - :snake: (**Python**).

To ensure that all libraries will work without any problems you will need at least **Python 3.10.0**. Moreover, you will **need** to install **several third party libraries**. To do this you have two possibilities: Either you **install** them **manually via Python's pip** or use **[Anaconda](https://www.anaconda.com/products/distribution)** and the **requirements.txt** in the folder **../.settings/** to install all dependencies at once.

Is everything ready? - Nothing forget? This will be a long journey without any breaks in between! Are you ready?!

## Chapter I: Across vallies and mountains...
After a long journey you are finally ready to enter the temple of **Marispace-X**. To enter you need to **find** and **call** the **main.py**.

<details>
<summary>Where to search? :confused:</summary>
<div align = "center"><img src = "/project/image(s)/readme-file/programm tree.png" alt = "programm tree"></div>
</details>

After you found the entrance you have to *Call It by Its Name*! Speak the spell!

```console
read@me:~$ python main.py
```

The gates open...

<details>
<summary>Reveal the truth! :open_mouth:</summary>
<div align = "center"><img src = "/project/image(s)/readme-file/gate to madness.png" alt = "gate to madness"></div>
</details>

The main goal of the UI is to be intutive and to simulate an normal console application. The difference to an normal bash is that commands are initiated with ```--```, e.g., ```--help```. The framework differentiated two kinds of commands, **single commands** and **command families**. A **single command** is a command which **stands for its own**, e.g, ```--build```. However, **command families** are commands which **only make sense to use if** they are **chained** together, e.g., ```--mount``` ```--config```. Thereby, the **order** of the commands **is irrelevant**: ```--mount``` ```--config``` and ```--config``` ```--mount``` will perform the same action. **Most** of the **commands** are commands **do not need** any **further parameters** because they **operate with the internal state** modified by the .config file. Those commands which need further parameters are shown under ```--help``` and are indicated with ```[<argument>, ...]```, e.g., ```--save``` ```--savestate``` ```[<argument>]```.

Finally! We are able to see the hearth of the framework! But, stop! - It's dangerous to go alone! Take this: ```--help```! Use this in case of any questions! :v:

## Chapter II: Time to meet the demons!
As mentioned in the last part, **most** of the **commands** do not need any further parameters because they **use the information stored in the .config file**, loaded at the beginning of the execution of an algorithm. The **.config file is the "head of everything"**. Therefore, the user has to load a .config file with ```--mount``` ```--config``` ```[<path to .config file>]```. The **.config file has** to **be valid** and has to **contain all parameters** which are needed **to execute** the desired **algorithm**. The following table lists all **mandatory parameters**:

| parameter name:             | purpose of the parameter:                                                                            |
| :-------------------------- | :--------------------------------------------------------------------------------------------------- |
| **.algorithm_name**         | **determines** the **algorithm** which should be **active**.                                         |
| **.algorithm_parameter(s)** | **determines** a/the **parameter(s)** which is/are **used** during the execution of .algorithm_name. |
| **.data**                   | **determines** a/the path(s) **where the data(s) is/are stored** (optional: set to ```undefined```). |

The parameters **.algorithm_parameter(s)** and **.data** are made to be extended with as many as need sub parameters. Thereby, the only constrain is to follow the file layout. It's recommanded to use the default layout and only to modify it if the default layout is not sufficient.

<details>
<summary>One .config file to rule them all! :smiling_imp:</summary>

The following example shows a default .config file for the [Advanced Route Skyline Computation (ARSC) algorithm](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.717.2623&rep=rep1&type=pdf).

<pre><code># Advanced Route Skyline Computation (ARSC): .config file:
.algorithm_name = "Advanced Route Skyline Computation (ARSC)"
.algorithm_parameter(s): {
    # H3 attribute(s):
    .H3_k_ring = 1
    .H3_resolution = 4

    # algorithm attribute(s):
    .source_node = (54.323334, 10.139444)
    .destination_node = (53.551086, 9.993682)
    .start_date = "2022-11-01 00:00:00"
    .SI_measurement(s) = [SI_TIME.SI_HOUR, SI_MASS.SI_METRIC_TON]
    .constant_speed(s) = 8.0

    # embedding attribute(s):
    .AS_dimension = 2
    .RNS_dimension = 8

    # data specific attribute(s):
    .latitude_delta = 0.08333206176
    .longitude_delta = 0.0833333358168602
    .time_period = 31

    # system attribute(s):
    .dynamic = False
    .preserve_data = True
}
.data: {
    .path_data = "code/data/data/.nc/data_file.nc"

    .path_VGD = "code/data/data/.nc/global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh_resample-1-day_??_2020-12-01_2021-01-01.nc"

    .path_write_to = "code/data/.result/.csv/"
    .path_image = "code/data/.result/.image/"

    .embedding = undefined # default: undefined or "code/data/.embedding/embedding_file.embedding"
}</code></pre>
</details>

To win the fight and to break the ban (find a solution) you need to speak the following:

```console
--mount --config <path to .config file>
```

<details>
<summary>Ah-bare-toh! :door:</summary>
<div align = "center"><img src = "/project/image(s)/readme-file/fight the demons (01).png" alt = "fight the demons (part 01)"></div>
</details>

```console
--algorithm --<name of algorithm>
```

<details>
<summary>Reducto! :hushed:</summary>
<div align = "center"><img src = "/project/image(s)/readme-file/fight the demons (02).png" alt = "fight the demons (part 02)"></div>
</details>

```console
--algorithm --visualize
```

<details>
<summary>Avada Kedavra! :skull:</summary>
<div align = "center"><img src = "/project/image(s)/readme-file/fight the demons (03).png" alt = "fight the demons (part 03)"></div>
</details>

Congratulation! You won the fight and solved your problem!

## Chapter IX III/IV: :sparkles:
The framework contains several other functions that wait to be explored! - Go and be curious! Don't worry they don't bite (hopefully)!

## Chapter XLII: What's now?
During your journey you found an or more enemy/ies that can not be defeated and now you need a stronger weapon! Therefore, you build an new one!

The application is highly modularizable and allows to be extended in many ways. **Every** new **algorithm** has to be **saved** into the folder **../algorithms/**. Thereby, **each algorithm** has to be **saved separately** in a **folder named with the short form of the algorithm**, e.g., the folder name for **Advanced Route Skyline Computation** would be **ARSC**. **Every algorithm** should be **extended** by the class ```ALGORITHM_ABSTRACT```. By extending this class you will **need to implement the method** ```execute_algorithm``` to match the signature of the algorithm classes. Finally, you will need to **implement and add further methods** into the main framework, if you want **that all functions will be active and usable** for your new algorithm. The following table lists all optional methods:

| command:                            |  method:           | purpose of the method:                                                                                 |
|  :--------------------------------- | :------------------| :----------------------------------------------------------------------------------------------------- |
| ```--algorithm``` ```--visualize``` | **visualize**      | determines **how** the result(s) of the calculation(s) should be **visualize**d.                       |
| intern management (not exposed)     | **write_to_**      | determines **how** the result(s) of the calculation(s) should be **save**d **into a file**.            |

Finally, **all methods** have to be **added** into the corresponding folders and **called** during runtime. Therefore, the **frame_main.py** has already a **default layout** which only **needs to be adapted**. For the sake of seamlessness all new methods have to be added in the way as the default algorithm (ARSC) it does. This **includes** a meaningful **error handling and reporting**. The framework will address most of the exception handling, only the new added methods have to be self monitored.

Now! Go! **Explore**, **build** and **create** something new! :v:

Where I was before I started to write this readme file... - Ah! Dear reader, if you...