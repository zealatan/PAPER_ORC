# my_paper Section Check

## Before Problem

Prior to this patch, the PaperNav parser only detected **2 sections** when parsing `my_paper.pdf`:

- `abstract`
- `references`

The root cause was that the paper uses **IEEE-style Roman numeral headings in ALL CAPS**:

```
I. INTRODUCTION
II. SYSTEM MODEL AND CHANNEL ESTIMATION
III. INTERNAL MECHANISM OF RELU DNNS
IV. ANALYSIS ON DL BASED CHANNEL ESTIMATION
V. ROBUSTNESS OF CHANNEL ESTIMATION TO MISMATCHED INFORMATION
VI. SIMULATION RESULTS
VII. CONCLUSIONS
REFERENCES
```

The pypdf text extractor introduces an additional artifact: **single uppercase letters are split from their word** by a space, producing:

```
I. I NTRODUCTION              (instead of I. INTRODUCTION)
II. S YSTEM MODEL AND ...     (instead of II. SYSTEM MODEL AND ...)
III. I NTERNAL MECHANISM ...  (instead of III. INTERNAL MECHANISM ...)
```

Neither the Roman numeral prefix nor the spaced-out heading text was matched by the original regex, which expected known mixed-case headings like `"Introduction"` or `"Related Work"`.

## After Patch

The patched parser now detects **9 sections**:

- `abstract`
- `introduction`
- `system_model`
- `internal_mechanism_of_relu_dnns`
- `analysis`
- `robustness_of_channel_estimation_to_mismatched_information`
- `experiment`
- `conclusion`
- `references`

## Section Table

| Section Key | Original Title | Character Count | Preview |
|---|---|---:|---|
| `abstract` | Abstract | 2,367 | Deep learning (DL) has emerged as an effective tool for channel estimation... |
| `introduction` | I. INTRODUCTION | 6,748 | Deep learning (DL) in wireless communications are making profound... |
| `system_model` | II. SYSTEM MODEL AND CHANNEL ESTIMATION | 4,897 | In this section, we firstly introduce the system model... |
| `internal_mechanism_of_relu_dnns` | III. INTERNAL MECHANISM OF RELU DNNS | 5,125 | In this section, a detailed description on the learning mechanism... |
| `analysis` | IV. ANALYSIS ON DL BASED CHANNEL ESTIMATION | 20,974 | Though the DL based channel estimation has shown excellent performance... |
| `robustness_of_channel_estimation_to_mismatched_information` | V. ROBUSTNESS OF CHANNEL ESTIMATION TO MISMATCHED INFORMATION | 8,114 | The optimality of the LMMSE and DL estimator is built on the assumption... |
| `experiment` | VI. SIMULATION RESULTS | 15,131 | In this section, computer-aided simulation is conducted... |
| `conclusion` | VII. CONCLUSIONS | 1,507 | In this paper, we have made the first attempt on interpreting... |
| `references` | REFERENCES | 6,321 | [1] Q. Hu and F. Gao... |
