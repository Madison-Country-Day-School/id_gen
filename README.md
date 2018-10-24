# id_gen

Bulk student ID generator

## Usage

Use the `--help` argument for help.
```
./id_gen.py --help
```

That produces:
```
usage: id_gen.py [-h] --template TEMPLATE --data DATA --images IMAGES
                 [--out OUT] [--debug]

Bulk generates student IDs from a template, csv data file, and images

optional arguments:
  -h, --help           show this help message and exit
  --template TEMPLATE  The path to the template SVG directory
  --data DATA          The path to the CSV data file
  --images IMAGES      The path to the directory of student photo images
  --out OUT            The path to the desired output directory. Defaults to
                       './id_gen_out'. Note: will fail if the directory (or
                       the tmp subdirectory) does not already exist.
  --debug              Enable debug output
```

Example command:
```
./id_gen.py --template=Template/ --data=data/students.csv --images=images/
```

### Example directory layout

**Template**:
```
...
└── Template
    ├── back.svg
    └── front.svg
```

**Data:**
```
...
└── data
    └── <name>.csv
```

**Images:**
```
...
└── images
    ├── 2019
    │   └── <name>.jpg
    ├── 2020
    │   └── <name>.jpg
    ├── 2021
    │   └── <name>.jpg
    └── 2022
        └── <name>.jpg
```
