# 07. The Final Expert Test

Before committing, they ask:

1. **"Can I explain this to a new hire in 30 seconds?"**
   - If not, the placement is too clever.

2. **"Will this break if we add 50 more devices?"**
   - Tests scalability of the pattern.

3. **"Can I write one Spark/SQL query to get all measurements across all devices?"**
   - Tests query predictability: `SELECT * WHERE topic LIKE '%/measurement/%'`

4. **"If this value is missing, which dashboard breaks?"**
   - Tests if criticality matches branch placement.

---