# Mini-CRM for Lead Distribution

Service for automatic distribution of lead contacts between operators by sources with consideration of weights and load limits.

## Requirements

- Python >= 3.12

## Installation

```bash
pip install -e .
```

## Running

```bash
uvicorn main:app --reload
```

After starting, the API will be available at `http://localhost:8000`
Swagger UI documentation: `http://localhost:8000/docs`

**Note:** Database file (`crm.db`) is created automatically on first startup.

## Data Model

### Entities and Relationships

1. **Operator**
   - `id` - unique identifier
   - `name` - operator name
   - `is_active` - active/inactive (can receive new contacts)
   - `max_load_limit` - maximum number of active contacts

2. **Source (Bot)**
   - `id` - unique identifier
   - `name` - source name
   - `description` - description (optional)

3. **OperatorSourceWeight (Operator-Source weight relationship)**
   - `id` - unique identifier
   - `operator_id` - reference to operator
   - `source_id` - reference to source
   - `weight` - numeric weight (competence) of operator for this source
   - Unique constraint on pair (operator_id, source_id)

4. **Lead**
   - `id` - unique identifier
   - `email` - lead email (unique, used to identify a single lead)

5. **Contact (Appeal)**
   - `id` - unique identifier
   - `lead_id` - reference to lead
   - `source_id` - reference to source
   - `operator_id` - reference to operator (can be NULL if no available operators)
   - `status` - contact status (default "active")
   - `created_at` - creation date and time

### Relationships

- Operator ↔ OperatorSourceWeight ↔ Source (many-to-many with weight)
- Lead → Contact (one-to-many)
- Source → Contact (one-to-many)
- Operator → Contact (one-to-many, nullable)

## Distribution Algorithm

### Lead Identification

Lead is identified by **email** (unique field). When registering a new contact:
- If a lead with such email already exists, the existing one is used
- If no lead exists, a new one is created

### Operator Weight Consideration by Sources

For each source, operator configuration with their weights is set via endpoint `POST /api/sources/{source_id}/operators`.

When distributing a contact:
1. All operators assigned to this source are retrieved
2. Sum of weights of available operators is calculated
3. Operator is selected probabilistically with probability `weight / sum_weights` using `random.choices()`

Example: for source A, operator1 has weight 10, operator2 has weight 30. Selection probability: 25% and 75% respectively.

### Load Limit Consideration

Operator load is defined as the number of **active contacts** (Contact with status='active') assigned to this operator.

When distributing a contact:
1. Only active operators are filtered (`is_active=True`)
2. For each operator, it is checked: current load < `max_load_limit`
3. Only operators that haven't exceeded the limit participate in distribution

### Handling Absence of Available Operators

If no suitable operators are available (all inactive or exceeded limit), the contact is created **without assigned operator** (`operator_id=NULL`). This allows saving the contact fact for subsequent manual processing or automatic processing when operators become available.

## API Endpoints

### Operators
- `POST /api/operators` - create operator
- `GET /api/operators` - list all operators
- `PATCH /api/operators/{id}` - update activity and/or load limit

### Sources
- `POST /api/sources` - create source
- `GET /api/sources` - list all sources
- `POST /api/sources/{source_id}/operators` - configure operators and weights for source

### Contacts
- `POST /api/contacts` - register contact (email, source_id)
- `GET /api/contacts` - list all contacts

### Leads
- `GET /api/leads` - list all leads with their contacts
