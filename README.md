# SLASCONE Python Licensing & Analytics Sample

This Python sample shows how to integrate SLASCONE into a software product. It demonstrates license management, entitlement management, usage analytics, floating licenses, and offline licensing in a Linux container and with the native SLASCONE client.

Going beyond simple API connectivity, this repository is designed as a practical integration reference for real-world licensing scenarios, including temporary offline operation, local license caching, and stable client identification in container environments.

It includes examples for the most important licensing, analytics, and resilience workflows:

* license activation and heartbeat
* floating session management
* license file validation and offline activation
* analytical, usage, and consumption heartbeats
* offline fallback using cached license data
* response and file integrity validation
* error handling and status reporting

For more information, see the [SLASCONE website](https://slascone.com/), the [Help Center](https://support.slascone.com/), and the [API Test Center](https://api365.slascone.com/swagger).

## Quick Start

Python 3.10 or newer is required for `slascone_client.py`.

Install Jupyter and the dependencies used by `licensing.ipynb`:

```bash
python -m pip install notebook requests
```

Start Jupyter from the repository root:

```bash
jupyter notebook
```

Open `slascone-sdk.ipynb` for the native offline-license example or `licensing.ipynb` for the SLASCONE REST API workflow.

The notebooks demonstrate integration patterns, but they are not production-ready services by themselves. Replace sample IDs, keys, customer data, and credentials before use.

## Table of Contents

* [Quick Start](#quick-start)
* [What This Sample Demonstrates](#what-this-sample-demonstrates)
* [Running the Notebooks](#running-the-notebooks)
* [Connecting to Your SLASCONE Environment](#connecting-to-your-slascone-environment)
* [Typical Licensing Flow](#typical-licensing-flow)
* [Offline Licensing and Freeride Period](#offline-licensing-and-freeride-period)
* [Container Licensing Example](#container-licensing-example)
* [Configuration and Storage](#configuration-and-storage)
* [Native Python Client](#native-python-client)
* [API Status Values](#api-status-values)
* [Project Structure](#project-structure)
* [Security](#security)
* [Further Reading](#further-reading)

## What This Sample Demonstrates

This sample application showcases the following key features of the SLASCONE licensing service.

### License Management and Entitlements

**License Activation (online)**

* Activates a license for a specific client
* Demonstrates how to activate a license key for the first time
* Handles activation responses and potential warnings or errors

**License Heartbeat**

* Sends periodic license verification requests to the SLASCONE server
* Retrieves the latest license information, features, limitations, and expiration data
* Provides the basis for cached license state and offline operation

**License Activation (offline)**

* Validates the digital signature of license files
* Reads and displays license information from signed XML files
* Supports inline activation or a separate activation file

**Offline License Support**

* Reads a signed license when temporarily disconnected from the SLASCONE service
* Verifies the license against product, client, release, and public-key settings
* Enforces the relevant license rules locally

**License Unassignment**

* Demonstrates how a license can be released from a client
* Allows a license to be transferred to a different client

### Floating License Management

**Session Management**

* Opens and closes licensing sessions for floating-license scenarios
* Supports limiting concurrent use across installed clients

**Session Closure**

* Releases floating licenses back to the pool
* Avoids license hoarding by inactive installations

### Security Features

**Client Identification**

* Uses a stable client or container identity strategy
* Secures licenses to a specific client or workload
* Avoids unstable identities when containers are recreated

**Digital Signature Validation**

* Verifies the authenticity of offline license files
* Prevents modification of license data
* Uses the configured public key and native validation library

## Running the Notebooks

Open `slascone-sdk.ipynb` for offline license validation or `licensing.ipynb` for the REST API workflow.

The bundled `SlasconeClient.so` is the native C library from the [SLASCONE-sdk](https://github.com/SLASCONE/SLASCONE-sdk) project. Use a compatible build for the target platform by passing `library_path` to `SlasconeClient`. If a native library does not work in your environment, verify that it matches the C ABI in `SlasconeClient.h` and is compatible with your operating system and architecture.

The native library is expected to implement ABI version 2. The Python wrapper rejects incompatible library builds.

## Connecting to Your SLASCONE Environment

By default, the notebooks contain or demonstrate values for a SLASCONE demo environment.

To connect the sample to your own SLASCONE environment, replace the relevant values in the notebooks and Python configuration:

* API base URL
* provisioning key
* ISV identifier
* product identifier
* license and client identifiers

You can find these values as explained in [API Fundamentals](https://support.slascone.com/hc/en-us/articles/360016153358). For meaningful testing and evaluation, your SLASCONE environment should have at least one active license.

> [!WARNING]
> Keep provisioning keys secure and do not embed production secrets in publicly accessible repositories. See [Secrets](https://support.slascone.com/hc/en-us/articles/7702036319261#secrets) in the SLASCONE Help Center for more information.

## Native Python Client

`SlasconeClient` provides a context-managed Python interface around the native C ABI:

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

    status = client.read_offline_license("license.xml")
    if status != SlasconeStatus.OK:
        raise RuntimeError(f"read_offline_license: {status.name}")

    status = client.check_offline_license()
    print(status.name)
```

## API Status Values

`SlasconeStatus` includes success and validation outcomes such as:

* `OK`
* `INVALID_ARGUMENT`
* `OUT_OF_MEMORY`
* `INTERNAL_ERROR`
* `NOT_CONFIGURED`
* `INVALID_PUBLIC_KEY`
* `FILE_ERROR`
* `INVALID_XML`
* `INVALID_SIGNATURE`
* `LICENSE_NOT_YET_VALID`
* `LICENSE_EXPIRED`
* `LICENSE_KEY_MISMATCH`
* `REVISION_MISMATCH`
* `CLIENT_ID_MISMATCH`
* `RELEASE_NOT_ALLOWED`
* `INVALID_LICENSE_DATES`
* `PRODUCT_ID_MISMATCH`

Compare status results instead of relying only on exceptions. Configuration and license-loading failures are returned as `SlasconeStatus` values.

## Project Structure

```text
SLASCONE-demo-python/
├── README.md
├── LICENSE
├── licensing.ipynb
├── slascone-sdk.ipynb
├── slascone_client.py
├── assets/
│   ├── ActivationFile.xml
│   └── License_...xml
└── slascone-client/
    ├── SlasconeClient.h
    └── SlasconeClient.so
```

| File | Purpose |
| --- | --- |
| `slascone-sdk.ipynb` | Demonstrates loading the native SLASCONE client and checking an offline license from Python. |
| `slascone_client.py` | Python `ctypes` wrapper around the SLASCONE native C ABI. |
| `licensing.ipynb` | Demonstrates license heartbeat, activation, and floating-session REST API workflows for Linux containers. |
| `slascone-client/SlasconeClient.h` | C ABI header for the native client. |
| `slascone-client/SlasconeClient.so` | Bundled Linux shared library. |
| `assets/` | Example activation and offline license XML files. |
| `LICENSE` | MIT license. |

## Security

* Keep provisioning keys and private keys out of source control.
* Prefer environment variables or a secret manager.
* Sanitize notebook output and remove executed notebook metadata containing account or licensing data.
* Review XML and notebook files before publishing because they may contain demo IDs or customer information.
* Never commit a real provisioning key or private credentials.

## Further Reading

* [API Test Center](https://api365.slascone.com/swagger)
* [What and How to Save in Your Client](https://support.slascone.com/hc/en-us/articles/7702036319261)
* [Digital Signature and Data Integrity](https://support.slascone.com/hc/en-us/articles/360016063637)
* [License Validation Fields](https://support.slascone.com/hc/en-us/articles/27831389148957-LICENSE-VALIDATION-FIELDS)
* [Error Handling](https://support.slascone.com/hc/en-us/articles/360016160398)
* [Product Analytics](https://support.slascone.com/hc/en-us/articles/360016055537)
* [Consumption-Based Limitations](https://support.slascone.com/hc/en-us/articles/360016057197)
* [C# NuGet Demo](https://github.com/SLASCONE/SLASCONE-demo-csharp-nuget)
* [WPF NuGet Demo](https://github.com/SLASCONE/SLASCONE-demo-wpf-nuget)
* [Java Demo](https://github.com/SLASCONE/SLASCONE-demo-java)
* [C++ Demo](https://github.com/SLASCONE/SLASCONE-demo-cpp)
