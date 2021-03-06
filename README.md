## SCRAMBLER (Short-reads CRISPR assembler): a tool for de novo CRISPR array reconstruction

**SCRAMBLER** is a tool for assembling CRISPR arrays from high-throughput short-read sequencing data.

Using amplicon sequencing data, SCRAMBLER generates a directed graph in which individual spacers are represented by the graph’s nodes, and the co-occurrences of spacers in two-spacer reads (i.e. pairs of spacers identified during sequencing) are represented by the graph’s edges. 

Artifacts that appear during PCR amplification (“PCR chimeras”) can be largely removed either via machine learning filtering or by applying a threshold that filters out sequences by their abundance.

Reconstruction of CRISPR arrays from the directed graph is done either with the “greedy” or the “soft” algorithm. "Greedy" algorithm reconstructs only the most abundant CRISPR arrays. "Soft" algorithm reconstructs all possible CRISPR array variants.


## Installation
* Install conda:
https://conda.io/projects/conda/en/latest/user-guide/install/
* Download SCRAMBLER:
https://github.com/biolab-tools/SCRAMBLER.git
* Create conda environment using `environment.yml` file:
```
> cd /PATH_TO_SCRAMBLER
> conda env create -f environment.yml
```
* Activate conda environment:
``` conda activate scrambler-env```
* Test SCRAMBLER installation:
``` python scrambler/run_scrambler.py -h```




## Usage
To run SCRAMBLER with the test data use:
``` 
python scrambler/run_scrambler.py \
-i examples/input_data/spacer_pairs_ecoliR1.txt \
-o examples/output/ \
-p examples/example_params.toml 
```
Required parameters:

`-i` input file with spacer pairs

`-o` path to output directory for assembled arrays

`-p` path to config file

### Input format
SCRAMBLER accepts pairs of spacers in the following format (space- or tab- delimited):
```
CAGCCGAAGCCAAAGGTGATGCCGAACACGCT GGCTCCCTGTCGGTTGTAATTGATAATGTTGA
AATAGCAATAGTCCATAGATTTGCGAAAACAG CAGCCGAAGCCAAAGGTGATGCCAAACACGCT
ACGTGGTCATGGGTGCTGCTGTTGCAGAGCCA AGCAGATACACGGCTTTGTATTCCGTGCGCCC
CTTTCGCAGACGCGCGGCGATACGCTCACGCA CAGCCGAAGCCAAAGGTGATGCCGAACACGCT
ACGTGGTCATGGGTGCTGCTGTTGCAGAGCCA AGCAGATACACGGCTTTGTATTCCGTGCGCCC
TCAGCTTTATAAATCCGGAGATACGGAAACTA GACTCACCCCGAAAGAGATTGCCAGCCAGCTT
AGCAGATACACGGCTTTGTATTCCGTGCGCCC AATAGCAATAGTCCATAGATTTGCGAAAACAG
GGAGTTCAGACATAGGTGGAATGATGGACTAC CCCGGTAGCCAGGTTTGCAACGCCTGAACCGA
GGCTCCCTGTCGGTTGTAATTGATAATGTTGA GTGTTTGCGGCATTAACGCTCACCAGCATTTC
GGAGTTCAGACATAGGTGGAATGATGGACTAC CCCGGTAGCCAGGTTTGCAACGCCTGAACCGA
TCAGCTTTATAAATCCGGAGATACGGAAACTA GACTCACCCCGAAAGAGATTGCCAGCCAGCTT
```
An example input file `spacer_pairs_ecoliR1.txt` can be found in `examples/input_data` directory.

### Config files
SCRAMBLER can create several assemblies with different parametres for the same input file. Information about assemblies is located in the config file. 

Here is an example config file `example_params.toml` for running two assemblies, with `soft` and `greedy` algorithms: 

```
[assembly.1]
use_logreg_filter = 1 
use_threshold_filter = 100
logreg_after_threshold = 0 
assembler = 'soft'


[assembly.2] 
use_logreg_filter = 1
use_threshold_filter = 100
logreg_after_threshold = 0
assembler = 'greedy'
```




Each assembly parameters section consists of assembly name (which should be written as `[assembly.N]`, where `N` is a unique integer ID) and 4 fields with parameters for graph filtering and arrays' assembly:

<table>
    <thead>
        <tr>
            <th colspan=2>use_logreg_filter</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="font-weight:bold">0</td>
            <td>LogReg filtering is not performed</td>
        </tr>
        <tr>
            <td style="font-weight:bold">1</td>
            <td>LogReg filtering is performed</td>
        </tr>
    </tbody>
</table>

<table>
    <thead>
        <tr>
            <th colspan=2>use_threshold_filter</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="font-weight:bold">0</td>
            <td>Threshold filtering is not performed</td>
        </tr>
        <tr>
            <td style="font-weight:bold">k</td>
            <td>Set integer <i>k</i> as a threshold value for filtering (i.e. ignore spacer pairs which appeared in the data less than <i>k</i> times)</td>
        </tr>
    </tbody>
</table>

<table>
    <thead>
        <tr>
            <th colspan=2>logreg_after_threshold</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="font-weight:bold">0</td>
            <td>LogReg is performed before threshold filtering</td>
        </tr>
        <tr>
            <td style="font-weight:bold">1</td>
            <td>LogReg is performed after threshold filtering</td>
        </tr>
    </tbody>
</table>


<table>
    <thead>
        <tr>
            <th colspan=2>assembler</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="font-weight:bold">'greedy'</td>
            <td>Assemble CRISPR arrays with 'greedy' algorithm </td>
        </tr>
        <tr>
            <td style="font-weight:bold">'soft'</td>
            <td>Assemble CRISPR arrays with 'soft' algorithm</td>
        </tr>
    </tbody>
</table>

File `example_params.toml` could be found in `examples` directory.
### Output format
SCRAMBLER creates two output files: a tab-separated file and a fasta-file. Examples of either files are shown below.

* **Tab-separated file.**
Output for each assembly method starts with a 5-line header with filtering and assembly options and assembled CRISPR arrays. CRISPR array lines contain @ARRAY key word, ID of array and sequences of spacers in the array.
```
@ASSEMBLER	soft
@FILTERING_OPTIONS
@THRESHOLD	100
@LOGREG	True
@LOGREG_AFTER_THRESHOLD	False

@ARRAY	1	CTTTCGCAGACGCGCGGCGATACGCTCACGCA	CAGCCGAAGCCAAAGGTGATGCCGAACACGCT	GGCTCCCTGTCGGTTGTAATTGATAATGTTGA	TTTGGATCGGGTCTGGAATTTCTGAGCGGTCGC	CGAATCGCGCATACCCTGCGCGTCGCCGCCTGC	TCAGCTTTATAAATCCGGAGATACGGAAACTA	GACTCACCCCGAAAGAGATTGCCAGCCAGCTT	CTGCTGGAGCTGGCTGCAAGGCAAGCCGCCCA	CCCACCAGCGCGTTTTTTGCCGGGGCCATAGT	GGAGTTCAGACATAGGTGGAATGATGGACTAC	CCCGGTAGCCAGGTTTGCAACGCCTGAACCGA	GCAACGACGGTGAGATTTCACGCCTGACGCTG
@ARRAY	2	GCAAAAACCGGGCAATCGCAAAAAGGCGTAAT	GTGTTTGCGGCATTAACGCTCACCAGCATTTC	ACGTGGTCATGGGTGCTGCTGTTGCAGAGCCA	AGCAGATACACGGCTTTGTATTCCGTGCGCCC	AATAGCAATAGTCCATAGATTTGCGAAAACAG	GAGCCTGACGAGACTACTGAGGCCGTTCTGTC
@ARRAY	3	GCAAAAACCGGGCAATCGCAAAAAGGCGTAAT	GTGTTTGCGGCATTAACGCTCACCAGCATTTC	ACGTGGTCATGGGTGCTGCTGTTGCAGAGCCA	AGCAGATACACGGCTTTGTATTCCGTGCGCCC	AATAGCAATAGTCCATAGATTTGCGAAAACAG	GTGTTTGCGGCATTAACGCTCACCAGCATTTC

@ASSEMBLER	greedy
@FILTERING_OPTIONS
@THRESHOLD	100
@LOGREG	True
@LOGREG_AFTER_THRESHOLD	False

@ARRAY	1	GCAAAAACCGGGCAATCGCAAAAAGGCGTAAT	GTGTTTGCGGCATTAACGCTCACCAGCATTTC	ACGTGGTCATGGGTGCTGCTGTTGCAGAGCCA	AGCAGATACACGGCTTTGTATTCCGTGCGCCC	AATAGCAATAGTCCATAGATTTGCGAAAACAG	GAGCCTGACGAGACTACTGAGGCCGTTCTGTC
@ARRAY	2	CTTTCGCAGACGCGCGGCGATACGCTCACGCA	CAGCCGAAGCCAAAGGTGATGCCGAACACGCT	GGCTCCCTGTCGGTTGTAATTGATAATGTTGA	TTTGGATCGGGTCTGGAATTTCTGAGCGGTCGC	CGAATCGCGCATACCCTGCGCGTCGCCGCCTGC	TCAGCTTTATAAATCCGGAGATACGGAAACTA	GACTCACCCCGAAAGAGATTGCCAGCCAGCTT	CTGCTGGAGCTGGCTGCAAGGCAAGCCGCCCA	CCCACCAGCGCGTTTTTTGCCGGGGCCATAGT	GGAGTTCAGACATAGGTGGAATGATGGACTAC	CCCGGTAGCCAGGTTTGCAACGCCTGAACCGA	GCAACGACGGTGAGATTTCACGCCTGACGCTG
```
* **FASTA-file.**
Each record in the file represents a spacer from the assembled arrays. A header contains information about filtering and assembly options and the corresponding spacer number of in an array.
```
>ASSEMBLER_soft|THRESHOLD_100|LOGREG_True|LOGREG_AFTER_THRESHOLD_False|ARRAY_1|SP_0
CTTTCGCAGACGCGCGGCGATACGCTCACGCA
>ASSEMBLER_soft|THRESHOLD_100|LOGREG_True|LOGREG_AFTER_THRESHOLD_False|ARRAY_1|SP_1
CAGCCGAAGCCAAAGGTGATGCCGAACACGCT
>ASSEMBLER_soft|THRESHOLD_100|LOGREG_True|LOGREG_AFTER_THRESHOLD_False|ARRAY_1|SP_2
GGCTCCCTGTCGGTTGTAATTGATAATGTTGA
>ASSEMBLER_soft|THRESHOLD_100|LOGREG_True|LOGREG_AFTER_THRESHOLD_False|ARRAY_1|SP_3
TTTGGATCGGGTCTGGAATTTCTGAGCGGTCGC
>ASSEMBLER_soft|THRESHOLD_100|LOGREG_True|LOGREG_AFTER_THRESHOLD_False|ARRAY_1|SP_4
CGAATCGCGCATACCCTGCGCGTCGCCGCCTGC
>ASSEMBLER_soft|THRESHOLD_100|LOGREG_True|LOGREG_AFTER_THRESHOLD_False|ARRAY_1|SP_5
TCAGCTTTATAAATCCGGAGATACGGAAACTA
>ASSEMBLER_soft|THRESHOLD_100|LOGREG_True|LOGREG_AFTER_THRESHOLD_False|ARRAY_1|SP_6
GACTCACCCCGAAAGAGATTGCCAGCCAGCTT
```
