--Q8 ORDER instrctors in ASCENDING order based on the grade they have given to
--students. For each instructor add the total grades, A, B, C. 
--Each line will consist of the Name of the instructor, the sum number of records 
--for each grade.
SELECT i.name, 
	SUM(CASE WHEN grade like 'A%' then 1 else 0 END) number_of_A,
	SUM(CASE WHEN grade like 'B%' then 1 else 0 END) number_of_B,
	SUM(CASE WHEN grade like 'C%' then 1 else 0 END) number_of_C,
	SUM(CASE WHEN grade like 'D%' then 1 else 0 END) number_of_D,
	SUM(CASE WHEN grade like 'E%' then 1 else 0 END) number_of_E,
	SUM(CASE WHEN grade like 'F%' then 1 else 0 END) number_of_F,
	SUM(CASE WHEN grade is NULL then 1 else 0 END) No_grade
FROM   takes t1
       JOIN teaches t2
         ON t1.course_id = t2.course_id
            AND t1.semester = t2.semester
            AND t1.year = t2.year
            AND t1.sec_id = t2.sec_id
		JOIN instructor i
		  ON i.ID = t2.ID
GROUP  BY i.name
ORDER  BY 2 ASC,
          3 ASC,
          4 ASC,
          5 ASC,
          6 ASC,
          7 ASC,
		  8 ASC



-- Q9 Create a view with the Buildings, the rooms (for each building)
--the total number of students and the total number of hours per semester
-- building|room_number|semester|tot_hours|tot_student_no
DROP VIEW IF EXISTS buildings;
CREATE VIEW buildings AS(
	SELECT	c.building,
			c.room_number,
			s.semester,
			Sum(Cast(( ( ( end_hr - start_hr ) * 60 ) + ( end_min - start_min ) ) /60 AS DECIMAL(4, 2))) tot_hours,
			Sum(tot_student_no) tot_student_no
	FROM   classroom c
			JOIN section s ON s.building = c.building and s.room_number = c.room_number
			JOIN time_slot t ON t.time_slot_id = s.time_slot_id
			LEFT JOIN (SELECT Count(*) tot_student_no,
							course_id,
							semester,
							year, 
					   		sec_id
						FROM   takes
						GROUP  BY course_id,
								semester,
								year,
								sec_id) t1
					ON t1.course_id = s.course_id
					AND t1.semester = s.semester
					AND t1.year = s.year  
					AND t1.sec_id = s.sec_id
	GROUP  BY c.building,
				c.room_number,
				s.semester
			);
SELECT * FROM buildings
ORDER BY 1,2,3

--Q10 create a view that will print the weekly schedule. The schedule will have for each semester/year 
--each week of the day, along with the courses that are being tought that day (time, room, instructor) 
--ordered by course start time
DROP VIEW IF EXISTS schedule;
CREATE VIEW schedule AS(
SELECT dept_name, 
	   title,
	   i1.year,
       i1.semester,
       i1.day,
       course_id,
       building,
       room_number,
       CONCAT(start_hr,':',start_min) AS start_time,
       CONCAT(end_hr,':',end_min)     AS end_time,
	   smst_rank, 
	   day_rank
FROM (SELECT s.*,
			day,
			CASE	WHEN day = 'M' THEN 1 
					WHEN day = 'T' THEN 2 
					WHEN day = 'W' THEN 3 
					WHEN day = 'R' THEN 4 
					WHEN day = 'F' THEN 5 END as day_rank,
			CASE WHEN LENGTH(CAST(start_hr AS VARCHAR(2))) = 1 THEN CONCAT('0',CAST(start_hr AS VARCHAR(2))) ELSE CAST(start_hr AS VARCHAR(2)) END start_hr, 
			CASE WHEN LENGTH(CAST(start_min AS VARCHAR(2))) = 1 THEN CONCAT('0',CAST(start_min AS VARCHAR(2))) ELSE CAST(start_min AS VARCHAR(2)) END start_min,
			CASE WHEN LENGTH(CAST(end_hr AS VARCHAR(2))) = 1 THEN CONCAT('0',CAST(end_hr AS VARCHAR(2))) ELSE CAST(end_hr AS VARCHAR(2)) END end_hr,
			CASE WHEN LENGTH(CAST(end_min AS VARCHAR(2))) = 1 THEN CONCAT('0',CAST(end_min AS VARCHAR(2))) ELSE CAST(end_min AS VARCHAR(2)) END end_min,
			CASE 
				WHEN semester = 'Spring' THEN 1
				WHEN semester = 'Summer' THEN 2
				WHEN semester = 'Fall' THEN 3
			END AS smst_rank,
	  		c.dept_name, 
	  		c.title
		FROM section s
			JOIN time_slot t ON t.time_slot_id = s.time_slot_id
	  		JOIN course c on s.course_id = c.course_id
		) i1 
);



SELECT dept_name, 
	   course_id,
	   title,
	   year,
       semester,
       day,
       building,
       room_number,
       start_time,
       end_time
FROM schedule
WHERE dept_name like '%'
ORDER  BY dept_name, 
	   	  year,
          smst_rank,
          day_rank,
          start_time 