DROP VIEW IF EXISTS director;
DROP VIEW IF EXISTS question5; 
DROP VIEW IF EXISTS question6; 

-- Q1 for each department with max salary > 42000 get the department name as 
-- well as the number of employees
SELECT dname,
       Count(*) number_of_employees
FROM   employee e
       LEFT JOIN department d
              ON d.dnumber = e.dno
WHERE  dno IN (SELECT DISTINCT dno
               FROM   employee
               WHERE  salary > 42000)
GROUP  BY dname; 

-- Q2 all employees from the department that the lowest salary employee is in
SELECT fname,
       lname
FROM   employee e1
WHERE  dno IN (SELECT DISTINCT dno
               FROM   employee
               WHERE  salary IN (SELECT Min(salary)
                                 FROM   employee)); 

-- Q3 find all employees who gain at least more than 5000 more than the average salary of the research department
SELECT fname
FROM   employee
WHERE  salary > (SELECT Avg(salary) + 5000 avg_dpt_salary
                 FROM   employee e,
                        department d
                 WHERE  e.dno = d.dnumber
                        AND d.dname = 'Research'); 

-- Q4 create a view with the name of the department, the name of the director and the salary of the director
CREATE VIEW director
AS
  SELECT dname,
         fname,
         salary
  FROM   department d,
         employee e
  WHERE  d.mgrssn = e.ssn;

SELECT * FROM   director; 

-- Q5 create a view with the name of the department, the name and surname of the director
-- the number of employees in the department and the number of project that are being controlled by it
CREATE VIEW question5
AS
  SELECT dname,
         fname,
         lname,
         numberofemployees,
         project_count
  FROM   department d
         LEFT JOIN employee dir ON dir.ssn = d.mgrssn
         LEFT JOIN (SELECT dno, Count(*) numberofemployees FROM employee GROUP BY dno) e ON e.dno = d.dnumber
         LEFT JOIN (SELECT Count(*) project_count, dnum FROM project GROUP BY dnum) p ON p.dnum = d.dnumber;

SELECT * FROM question5; 

-- Q6 create a view with the name of the project, the name of the department, the number of employees
-- the number of males employees, the number of female employees the total number of hours in the project
CREATE VIEW question6
AS
  WITH male
       AS (SELECT pno,
                  sex,
                  Count(*) male_count
           FROM   works_on w
                  JOIN (SELECT ssn, sex FROM employee WHERE  sex = 'M') e ON e.ssn = w.essn
           GROUP  BY pno,
                     sex),
       female
       AS (SELECT pno,
				  sex,
                  Count(*) female_count
           FROM   works_on w
                  JOIN (SELECT ssn, sex FROM employee WHERE  sex = 'F') e ON e.ssn = w.essn
           GROUP  BY pno,
                     sex)
  SELECT pname,
         dname,
         COALESCE (male_count, 0)
         + COALESCE (female_count, 0) num_of_employees,
         COALESCE (male_count, 0)     male_count,
         COALESCE (female_count, 0)   female_count,
         total_hours
  FROM   project p
         LEFT JOIN department d ON d.dnumber = p.dnum
         LEFT JOIN male m ON m.pno = p.pnumber
         LEFT JOIN female f ON f.pno = p.pnumber
         LEFT JOIN (SELECT Sum(hours) total_hours, pno FROM   works_on GROUP  BY pno) w ON w.pno = p.pnumber ;

SELECT * FROM question6;

-- Q7 find the top 3 employees who have worked the most in the company project's, the name of the departments they belong
-- and group the total number of hours per project
SELECT fname, lname, dname, total_hours, pname, hours
FROM (
	SELECT e.FNAME, e.LNAME, COALESCE(SUM(hours), 0) total_hours, essn, dno  
	FROM works_on w
	LEFT JOIN EMPLOYEE e on e.SSN = w.essn
	GROUP BY e.FNAME, e.LNAME, essn, dno
	ORDER BY COALESCE(SUM(hours), 0) DESC
	LIMIT 3) t
	JOIN works_on w on t.essn = w.essn
	JOIN department d on d.dnumber = t.dno
	JOIN project p on w.pno = p.pnumber
	
