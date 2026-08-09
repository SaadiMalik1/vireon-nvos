# I have an EEG file. What do I do?

## Step 1: Install VIREON

```bash
pip install vireon
```

## Step 2: Inspect your data

```bash
vireon inspect recording.edf
```

## Step 3: Run a quick validation

```bash
vireon validate recording.edf --method csp_lda --quick
```

## Step 4: View the report

```bash
vireon report <hash>
```

## Step 5: Run a full validation (when ready)

```bash
vireon validate recording.edf --method csp_lda --research
```
