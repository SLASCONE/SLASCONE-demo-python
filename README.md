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

### Analytics Capabilities

**Analytical Heartbeat**

* Sends general troubleshooting or application-level information
* Supports custom fields for application-specific metrics

**Feature Usage Tracking**

* Records which features are used
* Tracks feature usage frequency and patterns
* Provides insight for product development and pricing decisions

**Consumption Tracking**

* Reports usage-based metrics such as API calls or processed documents
* Supports pay-per-use licensing models
* Compares consumption with configured limitations

### Floating License Management

**Session Management**

* Opens and closes licensing sessions for floating-license scenarios
* Supports limiting concurrent use across installed clients

**Offline Session Handling**

* Reads and validates locally stored session data
* Helps maintain license compliance during temporary network interruptions

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

**Replay Protection**

* Uses nonce-based challenge-response protection where applicable

## Running the Notebooks

Open `slascone-sdk.ipynb` for offline license validation or `licensing.ipynb` for the REST API workflow.

The bundled `SlasconeClient.so` is a Linux build. Use a compatible build for the target platform by passing `library_path` to `SlasconeClient`. If a native library does not work in your environment, verify that it matches the C ABI in `SlasconeClient.h` and is compatible with your operating system and architecture.

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

## Typical Licensing Flow

A typical integration follows this sequence:

1. Identify the current client or device.
2. Activate the license for that client.
3. Send regular heartbeats to retrieve the latest license state.
4. Store the last valid license information locally.
5. Fall back to the cached license state during temporary connectivity issues.
6. Open and close sessions when using floating licenses.
7. Send analytical, usage, or consumption heartbeats as required by your product.
8. Unassign the license when needed.

This sample demonstrates these patterns in notebooks and a compact Python native-client wrapper so you can adapt the relevant parts to your own product.

## Offline Licensing and Freeride Period

The SLASCONE licensing system supports temporary and permanent offline scenarios. This is especially important for desktop applications, container workloads, and intermittently connected systems. For background, see [Offline and Connectivity](https://support.slascone.com/hc/en-us/sections/10214124833693).

### License Caching

During a successful license heartbeat, the application can save the latest license data locally. The cached information includes features, limitations, and expiration details and should be protected with digital signatures.

### Offline Validation

When the application cannot connect to the SLASCONE server, it can validate the cached or separately supplied license state before using it. The application should verify the digital signature and continue enforcing features, limitations, expiration dates, and client bindings from the validated state.

The native Python example demonstrates:

```python
status = client.read_offline_license("license.xml")
if status == SlasconeStatus.OK:
    status = client.check_offline_license("activation.xml")
```

Passing `None`, or omitting the activation path, selects inline activation.

### Freeride Period

The freeride period provides a configured grace period when heartbeats fail.

* It prevents immediate software lockout during temporary connectivity issues.
* It gives users time to restore connectivity.
* It tracks the time since the last successful heartbeat.
* A successful heartbeat resets the freeride state.
* Once the freeride period expires without a successful heartbeat, license enforcement takes effect.

Freeride periods are configured at the license edition level in the SLASCONE portal. Reserve freeride logic for true offline scenarios rather than every technical server error.

## Container Licensing Example

`licensing.ipynb` shows one approach for assigning a stable client identity in a Linux container:

1. Start a container with the required license or configuration available to the notebook.
2. Identify the host or container client ID.
3. Read the license and product configuration values.
4. Send a heartbeat.
5. Activate the client when the license is not yet known.
6. Open and close a floating session when required.

Example container command:

```bash
docker run --name slascone-demo \
  --env SLAS_LICENSE_ID=your-license-id \
  --volume C:\Projects\jovyan:/home/jovyan \
  -p 8888:8888 \
  jupyter/scipy-notebook:latest
```

Container IDs can change when containers are recreated. Decide whether the license should identify the container, an installed workload, or another stable client abstraction.

## Configuration and Storage

For detailed guidance on what should be stored locally, why it matters, and how cached license state supports offline and freeride scenarios, see [What to Store Locally in Your Client](https://support.slascone.com/hc/en-us/articles/7702036319261).

The native example uses locally available signed files rather than a general application-data folder. A production integration should persist only the license and session data required for its licensing model.

The following files are included as examples:

| File | Purpose |
| --- | --- |
| `assets/ActivationFile.xml` | Example activation data. |
| `assets/License_...xml` | Example signed offline license data. |
| `slascone-client/SlasconeClient.so` | Bundled Linux native client library. |
| `slascone-client/SlasconeClient.h` | C ABI header. |

Store cached license data in a persistent, access-controlled location appropriate for the target operating system. Verify signatures before use and remove stale or invalid state according to the licensing policy.

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
