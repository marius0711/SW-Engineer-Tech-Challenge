# Floy Technical Challenge

## Questions

**1. What were the reasons for your choice of API/protocol/architectural style used for the client-server communication?**

I chose a **RESTful API** over alternatives like **gRPC**, using **HTTP** as the communication protocol between the client and the server, for the following reasons:

- **Simplicity & Universality**: HTTP-based REST APIs are widely adopted, easy to understand, and compatible with virtually all networking environments.
- **Tooling Support**: The Python ecosystem offers excellent libraries like FastAPI and httpx, both of which natively support asynchronous programming.
- **Lightweight Communication**: REST introduces minimal overhead, making it ideal for prototyping and for transferring lightweight metadata.
- **Stateless Architecture**: REST’s stateless nature aligns perfectly with the system, where each metadata payload is self-contained and does not rely on session context.

Although **gRPC** provides advantages in terms of performance and strict schema enforcement, I considered it unnecessarily complex for this specific use case, which focuses on efficient and flexible metadata exchange.


**2.  As the client and server communicate over the internet in the real world, what measures would you take to secure the data transmission and how would you implement them?**

To securely transmit medical metadata in a production environment, I would implement the following measures:

---

### a) **Transport Layer Security (TLS)**

- Use **HTTPS** instead of HTTP to encrypt data in transit and protect against eavesdropping and man-in-the-middle (MITM) attacks.
- Implementation: Obtain and install SSL certificates (e.g., via Let’s Encrypt), and configure FastAPI/Uvicorn to run with TLS by specifying the SSL key and certificate file paths when starting the server.

---

### b) **Authentication & Authorization**

- Implement **token-based authentication** (e.g., JWT) to ensure only authorized clients can send data.
- Add **role-based access control (RBAC)** if different client roles exist (e.g., technicians, automated systems).

---

### c) **Data Validation & Input Sanitization**

- Leverage **Pydantic models** (already in use) to validate incoming metadata and prevent injection attacks or malformed payloads.

---

### d) **Network-level Security**

- Deploy the service behind a **reverse proxy** (e.g., NGINX or Caddy) or an **API gateway** with:
  - DDoS protection
  - Rate limiting
  - Request filtering
- Use **firewall rules**, **VPNs**, or **private networking** (e.g., AWS VPC or Docker network isolation) to limit server access.

---

### e) **Audit Logging & Monitoring**

- Log all requests and store metadata securely.
- Monitor logs for anomalies or unauthorized access attempts using tools like Prometheus/Grafana or ELK Stack.

---

### f) **Compliance**

- Ensure the system complies with relevant data protection regulations depending on the deployment region:
  - **GDPR** (EU)
  - **HIPAA** (US)
  - Local medical data laws (if applicable)


