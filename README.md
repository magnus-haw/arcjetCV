[![Documentation Status](https://readthedocs.org/projects/arcjetcv/badge/?version=latest)](https://arcjetcv.readthedocs.io/en/latest/?badge=latest)

-----

# arcjetCV

App to process arcjet videos and segment the edge of the shock and of the sample.

## Installation

Create conda environment:

    conda env create -f env/arcjetCV_env_[cpu/gpu].yml

and activate it:

    conda activate arcjetCV

then run the installation:

    pip install -e .

## Citing

If you use arcjetCV in your research, please use the following BibTeX entries to cite it:

```
@inbook{doi:10.2514/6.2023-1912,
author = {Alexandre Quintart and Magnus A. Haw},
title = {ArcjetCV: a new machine learning application for extracting time-resolved recession measurements from arc jet test videos},
booktitle = {AIAA SCITECH 2023 Forum},
doi = {10.2514/6.2023-1912},
URL = {https://arc.aiaa.org/doi/abs/10.2514/6.2023-1912},
eprint = {https://arc.aiaa.org/doi/pdf/10.2514/6.2023-1912},
}
```

## Run the GUI

You can now launch the GUI by running:

    conda activate arcjetCV
    arcjetCV

## Authors
Creator:  Magnus Haw

Contributors:
Alexandre Quintart
Federico Semeraro

## Legal / License
Copyright © 2024 United States Government as represented by the Administrator of the National Aeronautics and Space Administration.  All Rights Reserved.

Disclaimers

No Warranty: THE SUBJECT SOFTWARE IS PROVIDED "AS IS" WITHOUT ANY WARRANTY OF ANY KIND, EITHER EXPRESSED, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTY THAT THE SUBJECT SOFTWARE WILL CONFORM TO SPECIFICATIONS, ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR FREEDOM FROM INFRINGEMENT, ANY WARRANTY THAT THE SUBJECT SOFTWARE WILL BE ERROR FREE, OR ANY WARRANTY THAT DOCUMENTATION, IF PROVIDED, WILL CONFORM TO THE SUBJECT SOFTWARE. THIS AGREEMENT DOES NOT, IN ANY MANNER, CONSTITUTE AN ENDORSEMENT BY GOVERNMENT AGENCY OR ANY PRIOR RECIPIENT OF ANY RESULTS, RESULTING DESIGNS, HARDWARE, SOFTWARE PRODUCTS OR ANY OTHER APPLICATIONS RESULTING FROM USE OF THE SUBJECT SOFTWARE.  FURTHER, GOVERNMENT AGENCY DISCLAIMS ALL WARRANTIES AND LIABILITIES REGARDING THIRD-PARTY SOFTWARE, IF PRESENT IN THE ORIGINAL SOFTWARE, AND DISTRIBUTES IT "AS IS."

Waiver and Indemnity:  RECIPIENT AGREES TO WAIVE ANY AND ALL CLAIMS AGAINST THE UNITED STATES GOVERNMENT, ITS CONTRACTORS AND SUBCONTRACTORS, AS WELL AS ANY PRIOR RECIPIENT.  IF RECIPIENT'S USE OF THE SUBJECT SOFTWARE RESULTS IN ANY LIABILITIES, DEMANDS, DAMAGES, EXPENSES OR LOSSES ARISING FROM SUCH USE, INCLUDING ANY DAMAGES FROM PRODUCTS BASED ON, OR RESULTING FROM, RECIPIENT'S USE OF THE SUBJECT SOFTWARE, RECIPIENT SHALL INDEMNIFY AND HOLD HARMLESS THE UNITED STATES GOVERNMENT, ITS CONTRACTORS AND SUBCONTRACTORS, AS WELL AS ANY PRIOR RECIPIENT, TO THE EXTENT PERMITTED BY LAW.  RECIPIENT'S SOLE REMEDY FOR ANY SUCH MATTER SHALL BE THE IMMEDIATE, UNILATERAL TERMINATION OF THIS AGREEMENT. 
