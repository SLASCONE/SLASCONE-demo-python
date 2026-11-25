# SLASCONE Python Demo

Python examples for working with SLASCONE licensing in containers and for validating offline licenses with the native SLASCONE client.

> [!WARNING]
> The notebooks contain or demonstrate license, customer, and provisioning configuration values. Before publishing or sharing a fork, replace them with your own values and remove generated or sensitive output. Never commit a real provisioning key or private credentials.

## What this repository contains

| File | Purpose |
| --- | --- |
| `slascone-sdk.ipynb` | Demonstrates loading the native SLASCONE client and checking an offline license from Python. |
| `slascone_client.py` | Python `ctypes` wrapper around the SLASCONE native C ABI. |
| `licensing.ipynb` | Demonstrates license heartbeat, activation, and floating-session REST API workflows for Linux containers. |
| `slascone-client/SlasconeClient.h` | C ABI header for the native client. |
| `slascone-client/SlasconeClient.so` | Bundled Linux shared library. |
| `assets/` | Example activation and offline license XML files. |
| `LICENSE` | MIT license. |

## Offline license validation

`SlasconeClient` provides a context-managed Python interface for the native library:

```python
from pathlib import Path

from slascone_client import SlasconeClient, SlasconeStatus

with SlasconeClient(
    "your-product-id",
    library_path="/path/to/SlasconeClient.so",
) as client:
    configurations = (
        (client.set_client_id, "your-client-id"),
        (client.set_software_release, "1.0"),
        (client.set_pem_key, Path("public-key.pem").read_text(encoding="utf-8")),
    )

    for configure, value in configurations:
        status = configure(value)
        if status != SlasconeStatus.OK:
            raise RuntimeError(f"{configure.__name__}: {status.name}")

    status = client.check_offline_license("license.xml")
    print(status.name)
```

To provide a separate activation file:

```python
status = client.check_offline_license(
    "license.xml",
    "activation.xml",
)
```

Passing `None`, or omitting the activation path, selects inline activation.

The native library is expected to implement ABI version 1. The Python wrapper rejects incompatible library builds.

## Running the notebooks

Python 3.10 or newer is required for `slascone_client.py`.

Install Jupyter and the notebook dependency used by `licensing.ipynb`:

```bash
python -m pip install notebook requests
```

Start Jupyter from the repository root:

```bash
jupyter notebook
```

Open `slascone-sdk.ipynb` for the native client example or `licensing.ipynb` for the SLASCONE REST API workflow.

The bundled `SlasconeClient.so` is a Linux build. Use a compatible build for the target platform by passing `library_path` to `SlasconeClient`. If a native library does not work in your environment, verify that it matches the C ABI in `SlasconeClient.h` and is compatible with your operating system and architecture.

## Container licensing example

`licensing.ipynb` shows one approach for assigning a stable client identity in a Linux container:

1. Start a container with the required license or configuration available to the notebook.
2. Identify the host/container client ID.
3. Read the license and product configuration values.
4. Send a heartbeat.
5. Activate the client when the license is not yet known.
6. Open and close a floating session when required.

The notebook uses the SLASCONE REST API base URL and provisioning endpoints. Configure all IDs and credentials locally; do not use sample credentials in production.

Example container command:

```bash
docker run --name slascone-demo \
  --env SLAS_LICENSE_ID=your-license-id \
  --volume C:\Projects\jovyan:/home/jovyan \
  -p 8888:8888 \
  jupyter/scipy-notebook:latest
```

Adjust the volume path for your environment. Container IDs can change when containers are recreated, so decide whether the license should identify the container, an installed workload, or another stable client abstraction.

## API status values

`SlasconeStatus` includes success and validation outcomes such as:

- `OK`
- `INVALID_ARGUMENT`
- `NOT_CONFIGURED`
- `INVALID_PUBLIC_KEY`
- `FILE_ERROR`
- `INVALID_XML`
- `INVALID_SIGNATURE`
- `LICENSE_NOT_YET_VALID`
- `LICENSE_EXPIRED`
- `LICENSE_KEY_MISMATCH`
- `REVISION_MISMATCH`
- `CLIENT_ID_MISMATCH`
- `RELEASE_NOT_ALLOWED`

Compare status results instead of relying only on exceptions. Configuration and license-loading failures are returned as `SlasconeStatus` values.

## Security

- Keep provisioning keys and private keys out of source control.
- Prefer environment variables or a secret manager.
- Sanitize notebook output and remove executed notebook metadata containing account or licensing data.
- Review the XML and notebook files before publishing because they may contain demo IDs or customer information.

## License

This project is licensed under the [MIT License](LICENSE).
