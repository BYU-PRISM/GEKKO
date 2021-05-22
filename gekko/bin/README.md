The local executables are used when option `remote=False` when creating the Gekko model.

```python
m = GEKKO(remote=False)
```

Versions of the local executable include:

- Windows (32 or 64 bit): apm.exe
- Linux (64 bit): apm
- MacOS (64 bit): apm_mac
- Linux ARM (Raspberry Pi): apm_arm

Set chmod u+x on Linux or MacOS to allow local execution, if there is a permission issue.
