# full_lenient 的错误样本（每类随机抽 15 条，seed=0）

## 执行报错/列名不存在（共 126 条）

- 问题: What is the total number of countries where Spanish is spoken by the largest percentage of people?
  - db: world_1
  - 标准: `SELECT count(*) ,   max(Percentage) FROM countrylanguage WHERE LANGUAGE  =  "Spanish" GROUP BY CountryCode`
  - 预测: `SELECT country FROM countrylanguage WHERE language = 'Spanish' AND percentage = (SELECT max(percentage) FROM countrylanguage WHERE language = 'Spanish')`
  - 原因: pred_error: no such column: country

- 问题: What are the id and names of the countries which have more than 3 car makers or produce the 'fiat' model?
  - db: car_1
  - 标准: `SELECT T1.countryId ,  T1.CountryName FROM Countries AS T1 JOIN CAR_MAKERS AS T2 ON T1.CountryId  =  T2.Country GROUP BY T1.countryId HAVING count(*)  >  3 UNION SELECT T1.countryId ,  T1.CountryName FROM Countries AS T1 JOIN CAR_MAKERS AS T2 ON T1.CountryId  =  T2.Country JOIN MODEL_LIST AS T3 ON T2.Id  =  T3.Maker WHERE T3.Model  =  'fiat';`
  - 预测: `SELECT T1.CountryId , T1.CountryName FROM countries AS T1 JOIN car_makers AS T2 ON T1.CountryId = T2.Country WHERE T2.Count > 3 UNION SELECT T1.CountryId , T1.CountryName FROM countries AS T1 JOIN model_list AS T2 ON T1.CountryId = T2.Country WHERE T2.Model = 'fiat'`
  - 原因: pred_error: no such column: T2.Country

- 问题: Give the mean life expectancy of countries in which English is not the official language.
  - db: world_1
  - 标准: `SELECT avg(LifeExpectancy) FROM country WHERE Name NOT IN (SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "English" AND T2.IsOfficial  =  "T")`
  - 预测: `SELECT avg(LifeExpectancy) FROM country WHERE Language != 'English'`
  - 原因: pred_error: no such column: Language

- 问题: Return the names of friends of the high school student Kyle.
  - db: network_1
  - 标准: `SELECT T3.name FROM Friend AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id JOIN Highschooler AS T3 ON T1.friend_id  =  T3.id WHERE T2.name  =  "Kyle"`
  - 预测: `SELECT T2.name FROM highschooler AS T1 JOIN friend AS T2 ON T1.id = T2.friend_id WHERE T1.name = 'Kyle'`
  - 原因: pred_error: no such column: T2.name

- 问题: Which shop has the most employees? Give me the shop name.
  - db: employee_hire_evaluation
  - 标准: `SELECT t2.name FROM hiring AS t1 JOIN shop AS t2 ON t1.shop_id  =  t2.shop_id GROUP BY t1.shop_id ORDER BY count(*) DESC LIMIT 1`
  - 预测: `SELECT T2.name FROM evaluation AS T1 JOIN shop AS T2 ON T1.shop_id = T2.shop_id GROUP BY T1.shop_id ORDER BY count(*) DESC LIMIT 1`
  - 原因: pred_error: no such column: T1.shop_id

- 问题: List the maximum weight and type for each type of pet.
  - db: pets_1
  - 标准: `SELECT max(weight) ,  petType FROM pets GROUP BY petType`
  - 预测: `SELECT max(weight) , pet_type FROM pets GROUP BY pet_type`
  - 原因: pred_error: no such column: pet_type

- 问题: What is the largest amount of horsepower for the models with 3 cylinders and what make is it?
  - db: car_1
  - 标准: `SELECT T2.horsepower ,  T1.Make FROM CAR_NAMES AS T1 JOIN CARS_DATA AS T2 ON T1.MakeId  =  T2.Id WHERE T2.cylinders  =  3 ORDER BY T2.horsepower DESC LIMIT 1;`
  - 预测: `SELECT max(T2.Horsepower) , T1.Make FROM car_names AS T1 JOIN cars_data AS T2 ON T1.ModelId = T2.ModelId WHERE T1.Cylinders = 3`
  - 原因: pred_error: no such column: T1.Cylinders

- 问题: Find the first names of owners living in Virginia and the names of dogs they own.
  - db: dog_kennels
  - 标准: `SELECT T1.first_name ,  T2.name FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id  =  T2.owner_id WHERE T1.state  =  'Virginia'`
  - 预测: `SELECT T2.first_name , T3.name FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id = T2.owner_id WHERE T1.state = 'VA'`
  - 原因: pred_error: no such column: T2.first_name

- 问题: Find the name of the winner who has the highest rank points and participated in the Australian Open tourney.
  - db: wta_1
  - 标准: `SELECT winner_name FROM matches WHERE tourney_name  =  'Australian Open' ORDER BY winner_rank_points DESC LIMIT 1`
  - 预测: `SELECT T1.winner_name FROM matches AS T1 JOIN players AS T2 ON T1.winner_id = T2.player_id WHERE T1.tournament_name = 'Australian Open' ORDER BY T1.winning_points DESC LIMIT 1`
  - 原因: pred_error: no such column: T1.tournament_name

- 问题: What are the names of players who won in both 2013 and 2016?
  - db: wta_1
  - 标准: `SELECT winner_name FROM matches WHERE YEAR  =  2013 INTERSECT SELECT winner_name FROM matches WHERE YEAR  =  2016`
  - 预测: `SELECT T1.first_name , T1.last_name FROM players AS T1 JOIN matches AS T2 ON T1.player_id = T2.winner WHERE T2.year = 2013 INTERSECT SELECT T1.first_name , T1.last_name FROM players AS T1 JOIN matches AS T2 ON T1.player_id = T2.winner WHERE T2.year = 2016`
  - 原因: pred_error: no such column: T2.winner

- 问题: List all airline names and their abbreviations in "USA".
  - db: flight_2
  - 标准: `SELECT Airline ,  Abbreviation FROM AIRLINES WHERE Country  =  "USA"`
  - 预测: `SELECT T1.Airline , T1.Abbreviation FROM airlines AS T1 JOIN airports AS T2 ON T1.uid = T2.Uid WHERE T2.CountryAbbrev = "USA"`
  - 原因: pred_error: no such column: T2.Uid

- 问题: Which professionals have done at least two treatments? List the professional's id, role, and first name.
  - db: dog_kennels
  - 标准: `SELECT T1.professional_id ,  T1.role_code ,  T1.first_name FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id  =  T2.professional_id GROUP BY T1.professional_id HAVING count(*)  >=  2`
  - 预测: `SELECT T1.professional_id , T1.role_code , T2.first_name FROM Professionals AS T1 JOIN Treatment_Types AS T2 ON T1.professional_id = T2.treatment_id GROUP BY T1.professional_id HAVING count(*) >= 2`
  - 原因: pred_error: no such column: T2.first_name

- 问题: What are the codes of the countries that do not speak English and whose government forms are not Republic?
  - db: world_1
  - 标准: `SELECT Code FROM country WHERE GovernmentForm != "Republic" EXCEPT SELECT CountryCode FROM countrylanguage WHERE LANGUAGE  =  "English"`
  - 预测: `SELECT code FROM country EXCEPT SELECT T1.code FROM country AS T1 JOIN countrylanguage AS T2 ON T1.code = T2.CountryCode WHERE T2.language = "English" OR T1政府形式 != "Republic"`
  - 原因: pred_error: no such column: T1政府形式

- 问题: Find the number of cities in each district whose population is greater than the average population of cities?
  - db: world_1
  - 标准: `SELECT count(*) ,  District FROM city WHERE Population  >  (SELECT avg(Population) FROM city) GROUP BY District`
  - 预测: `SELECT count(*) , district FROM city WHERE population > ( SELECT avg(population) FROM city ) GROUP BY chart_district`
  - 原因: pred_error: no such column: chart_district

- 问题: Which distinctive models are produced by maker with the full name General Motors or weighing more than 3500?
  - db: car_1
  - 标准: `SELECT DISTINCT T2.Model FROM CAR_NAMES AS T1 JOIN MODEL_LIST AS T2 ON T1.Model  =  T2.Model JOIN CAR_MAKERS AS T3 ON T2.Maker  =  T3.Id JOIN CARS_DATA AS T4 ON T1.MakeId  =  T4.Id WHERE T3.FullName  =  'General Motors' OR T4.weight  >  3500;`
  - 预测: `SELECT DISTINCT T1.Model FROM model_list AS T1 JOIN car_makers AS T2 ON T1.Maker = T2.Id WHERE T2.FullName = "General Motors" OR T1.Weight > 3500`
  - 原因: pred_error: no such column: T1.Weight

## 结果错误/结构齐全，列或条件不对（共 121 条）

- 问题: Show name of all students who have some friends and also are liked by someone else.
  - db: network_1
  - 标准: `SELECT T2.name FROM Friend AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id INTERSECT SELECT T2.name FROM Likes AS T1 JOIN Highschooler AS T2 ON T1.liked_id  =  T2.id`
  - 预测: `SELECT T1.name FROM highschooler AS T1 JOIN friend AS T2 ON T1.id = T2.student_id INTERSECT SELECT T1.name FROM highschooler AS T1 JOIN likes AS T2 ON T1.id = T2.student_id`
  - 原因: wrong_result

- 问题: Which student has enrolled for the most times in any program? List the id, first name, middle name, last name, the number of enrollments and student id.
  - db: student_transcripts_tracking
  - 标准: `SELECT T1.student_id ,  T1.first_name ,  T1.middle_name ,  T1.last_name ,  count(*) ,  T1.student_id FROM Students AS T1 JOIN Student_Enrolment AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_id ORDER BY count(*) DESC LIMIT 1`
  - 预测: `SELECT T1.student_id , T1.first_name , T1.middle_name , T1.last_name , count(*) FROM Students AS T1 JOIN Student_Enrolment AS T2 ON T1.student_id = T2.student_id GROUP BY T1.student_id ORDER BY count(*) DESC LIMIT 1`
  - 原因: wrong_result

- 问题: Give the total population and average surface area corresponding to countries in North America that have a surface area greater than 3000 .
  - db: world_1
  - 标准: `select sum(population) ,  avg(surfacearea) from country where continent  =  "north america" and surfacearea  >  3000`
  - 预测: `SELECT sum(population) , avg(surfacearea) FROM country WHERE continent = 'North America' AND surfacearea > 3000`
  - 原因: wrong_result

- 问题: What are the first name and last name of the professionals who have done treatment with cost below average?
  - db: dog_kennels
  - 标准: `SELECT DISTINCT T1.first_name ,  T1.last_name FROM Professionals AS T1 JOIN Treatments AS T2 WHERE cost_of_treatment  <  ( SELECT avg(cost_of_treatment) FROM Treatments )`
  - 预测: `SELECT T2.first_name , T2.last_name FROM treatments AS T1 JOIN professionals AS T2 ON T1.professional_id = T2.professional_id WHERE T1.cost_of_treatment < ( SELECT avg(cost_of_treatment) FROM treatments )`
  - 原因: wrong_result

- 问题: Find the last name of the students who currently live in the state of North Carolina but have not registered in any degree program.
  - db: student_transcripts_tracking
  - 标准: `SELECT T1.last_name FROM Students AS T1 JOIN Addresses AS T2 ON T1.current_address_id  =  T2.address_id WHERE T2.state_province_county  =  'NorthCarolina' EXCEPT SELECT DISTINCT T3.last_name FROM Students AS T3 JOIN Student_Enrolment AS T4 ON T3.student_id  =  T4.student_id`
  - 预测: `SELECT T1.last_name FROM students AS T1 JOIN addresses AS T2 ON T1.current_address_id = T2.address_id WHERE T2.state_province_county = 'North Carolina' EXCEPT SELECT T1.last_name FROM students AS T1 JOIN student_enrolment AS T2 ON T1.student_id = T2.student_id`
  - 原因: wrong_result

- 问题: Find the id of students who do not have a cat pet.
  - db: pets_1
  - 标准: `SELECT stuid FROM student EXCEPT SELECT T1.stuid FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid  =  T2.stuid JOIN pets AS T3 ON T3.petid  =  T2.petid WHERE T3.pettype  =  'cat'`
  - 预测: `SELECT StuID FROM Student EXCEPT SELECT T1.StuID FROM Has_pet AS T1 JOIN Pets AS T2 ON T1.petid = T2.petid WHERE T2.PetType = "Cat"`
  - 原因: wrong_result

- 问题: What is the first name and country code of the oldest player?
  - db: wta_1
  - 标准: `SELECT first_name ,  country_code FROM players ORDER BY birth_date LIMIT 1`
  - 预测: `SELECT first_name , country_code FROM players ORDER BY birth_date DESC LIMIT 1`
  - 原因: wrong_result

- 问题: What are the countries that are not playing cartoons written by Todd Casey?
  - db: tvshow
  - 标准: `SELECT country FROM TV_Channel EXCEPT SELECT T1.country FROM TV_Channel AS T1 JOIN cartoon AS T2 ON T1.id = T2.Channel WHERE T2.written_by  =  'Todd Casey'`
  - 预测: `SELECT country FROM tv_channel EXCEPT SELECT T1.country FROM tv_channel AS T1 JOIN Cartoon AS T2 ON T1.id = T2.channel WHERE T2.directed_by = "Todd Casey"`
  - 原因: wrong_result

- 问题: Find the first name of the students who permanently live in the country Haiti or have the cell phone number 09700166582 .
  - db: student_transcripts_tracking
  - 标准: `select t1.first_name from students as t1 join addresses as t2 on t1.permanent_address_id  =  t2.address_id where t2.country  =  'haiti' or t1.cell_mobile_number  =  '09700166582'`
  - 预测: `SELECT T1.first_name FROM students AS T1 JOIN addresses AS T2 ON T1.permanent_address_id = T2.address_id WHERE T2.country = 'Haiti' OR T1.cell_mobile_number = '09700166582'`
  - 原因: wrong_result

- 问题: What's the name of the course with most number of enrollments?
  - db: student_transcripts_tracking
  - 标准: `SELECT  T1.course_name FROM Courses AS T1 JOIN Student_Enrolment_Courses AS T2 ON T1.course_id  =  T2.course_id GROUP BY T1.course_name ORDER BY count(*) DESC LIMIT 1`
  - 预测: `SELECT T1.course_name FROM courses AS T1 JOIN student_enrolment_courses AS T2 ON T1.course_id = T2.course_id GROUP BY T1.course_id ORDER BY count(*) DESC LIMIT 1`
  - 原因: wrong_result

- 问题: How much does the most recent treatment cost?
  - db: dog_kennels
  - 标准: `SELECT cost_of_treatment FROM Treatments ORDER BY date_of_treatment DESC LIMIT 1`
  - 预测: `SELECT max(cost_of_treatment) FROM treatments ORDER BY date_of_treatment DESC LIMIT 1`
  - 原因: wrong_result

- 问题: What is the name of the conductor who has conducted the most orchestras?
  - db: orchestra
  - 标准: `SELECT T1.Name FROM conductor AS T1 JOIN orchestra AS T2 ON T1.Conductor_ID  =  T2.Conductor_ID GROUP BY T2.Conductor_ID ORDER BY COUNT(*) DESC LIMIT 1`
  - 预测: `SELECT T1.Name FROM conductor AS T1 JOIN orchestra AS T2 ON T1.Conductor_ID = T2.Conductor_ID GROUP BY T1.Name ORDER BY COUNT(*) DESC LIMIT 1`
  - 原因: wrong_result

- 问题: Show the ids of high schoolers who have friends and are also liked by someone else.
  - db: network_1
  - 标准: `SELECT student_id FROM Friend INTERSECT SELECT liked_id FROM Likes`
  - 预测: `SELECT T1.id FROM Highschooler AS T1 JOIN Friend AS T2 ON T1.ID = T2.student_id INTERSECT SELECT T1.id FROM Highschooler AS T1 JOIN Likes AS T2 ON T1.ID = T2.student_id`
  - 原因: wrong_result

- 问题: What are the first names of all players, and their average rankings?
  - db: wta_1
  - 标准: `SELECT avg(ranking) ,  T1.first_name FROM players AS T1 JOIN rankings AS T2 ON T1.player_id  =  T2.player_id GROUP BY T1.first_name`
  - 预测: `SELECT T1.first_name , avg(T2.ranking) FROM players AS T1 JOIN rankings AS T2 ON T1.player_id = T2.player_id GROUP BY T1.player_id`
  - 原因: wrong_result

- 问题: Describe the section h.
  - db: student_transcripts_tracking
  - 标准: `SELECT section_description FROM Sections WHERE section_name  =  'h'`
  - 预测: `SELECT section_name FROM sections WHERE section_name = 'h'`
  - 原因: wrong_result

## 执行报错/表名不存在（共 14 条）

- 问题: Show the property type descriptions of properties belonging to that code.
  - db: real_estate_properties
  - 标准: `SELECT T2.property_type_description FROM Properties AS T1 JOIN Ref_Property_Types AS T2 ON T1.property_type_code  =  T2.property_type_code GROUP BY T1.property_type_code`
  - 预测: `SELECT T2.property_type_description FROM Ref_Property_Types AS T1 JOIN Property_Types AS T2 ON T1.property_type_code = T2.property_type_code`
  - 原因: pred_error: no such table: Property_Types

- 问题: What is the name of the winner who has won the most matches, and how many rank points does this player have?
  - db: wta_1
  - 标准: `SELECT winner_name ,  winner_rank_points FROM matches GROUP BY winner_name ORDER BY count(*) DESC LIMIT 1`
  - 预测: `SELECT T1.winner_name , T1.winner_rank_points FROM winners AS T1 JOIN MATCHES AS T2 ON T1.tourney_id = T2.tourney_id GROUP BY T1.winner_name ORDER BY count(*) DESC LIMIT 1`
  - 原因: pred_error: no such table: winners

- 问题: Show the student IDs and numbers of friends corresponding to each.
  - db: network_1
  - 标准: `SELECT student_id ,  count(*) FROM Friend GROUP BY student_id`
  - 预测: `SELECT T1.student_id , count(*) FROM Student AS T1 JOIN Friend AS T2 ON T1.ID = T2.student_id GROUP BY T1.student_id`
  - 原因: pred_error: no such table: Student

- 问题: What are the names and release years for all the songs of the youngest singer?
  - db: concert_singer
  - 标准: `SELECT song_name ,  song_release_year FROM singer ORDER BY age LIMIT 1`
  - 预测: `SELECT T2.Song_Name , T2.Song_release_year FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID ORDER BY T1.Age ASC LIMIT 1`
  - 原因: pred_error: no such table: song

- 问题: What model has the most different versions?
  - db: car_1
  - 标准: `SELECT Model FROM CAR_NAMES GROUP BY Model ORDER BY count(*) DESC LIMIT 1;`
  - 预测: `SELECT T2.Model FROM car_versions AS T1 JOIN model_list AS T2 ON T1.Model = T2.Modelid GROUP BY T1.Model ORDER BY COUNT(*) DESC LIMIT 1`
  - 原因: pred_error: no such table: car_versions

- 问题: What are the last name of the students who live in North Carolina but have not registered in any degree programs?
  - db: student_transcripts_tracking
  - 标准: `SELECT T1.last_name FROM Students AS T1 JOIN Addresses AS T2 ON T1.current_address_id  =  T2.address_id WHERE T2.state_province_county  =  'NorthCarolina' EXCEPT SELECT DISTINCT T3.last_name FROM Students AS T3 JOIN Student_Enrolment AS T4 ON T3.student_id  =  T4.student_id`
  - 预测: `SELECT T1.last_name FROM students AS T1 JOIN addresses AS T2 ON T1.current_address_id = T2.address_id WHERE T2.state_province_county = 'North Carolina' EXCEPT SELECT T4.last_name FROM students AS T1 JOIN student_enrolment AS T2 ON T1.student_id = T2.student_id JOIN degrees AS T3 ON T2.degree_program_id = T3.degree_program_id JOIN students AS T4 ON T2.student_id = T4.student_id WHERE T3.program_name = 'Certificate'`
  - 原因: pred_error: no such table: degrees

- 问题: Show names, results and bulgarian commanders of the battles with no ships lost in the 'English Channel'.
  - db: battle_death
  - 标准: `SELECT name ,  RESULT ,  bulgarian_commander FROM battle EXCEPT SELECT T1.name ,  T1.result ,  T1.bulgarian_commander FROM battle AS T1 JOIN ship AS T2 ON T1.id  =  T2.lost_in_battle WHERE T2.location  =  'English Channel'`
  - 预测: `SELECT name , result , bulgarian_commander FROM battle WHERE id NOT IN ( SELECT T1.id FROM ship AS T1 JOIN LOCATION AS T2 ON T1.location = T2.id WHERE T2.name = 'English Channel' )`
  - 原因: pred_error: no such table: LOCATION

- 问题: Which model has the most version(make) of cars?
  - db: car_1
  - 标准: `SELECT Model FROM CAR_NAMES GROUP BY Model ORDER BY count(*) DESC LIMIT 1;`
  - 预测: `SELECT T2.Model FROM car_versions AS T1 JOIN model_list AS T2 ON T1.Model = T2.Modelid GROUP BY T2.Model ORDER BY COUNT(*) DESC LIMIT 1`
  - 原因: pred_error: no such table: car_versions

- 问题: What is the average miles per gallon(mpg) of the cars with 4 cylinders?
  - db: car_1
  - 标准: `SELECT avg(mpg) FROM CARS_DATA WHERE Cylinders  =  4;`
  - 预测: `SELECT avg(mpg) FROM cars WHERE cylinders = 4`
  - 原因: pred_error: no such table: cars

- 问题: What are the population, name and leader of the country with the largest area?
  - db: world_1
  - 标准: `SELECT Name ,  population ,  HeadOfState FROM country ORDER BY SurfaceArea DESC LIMIT 1`
  - 预测: `SELECT T1.population , T1.name , T3.HeadOfState FROM country AS T1 JOIN countrylanguage AS T2 ON T1.code = T2.countrycode JOIN world AS T3 ON T1.surfacearea = T3.GNPOLD ORDER BY T1.surfacearea DESC LIMIT 1`
  - 原因: pred_error: no such table: world

- 问题: Find the name of tourney that has more than 10 matches.
  - db: wta_1
  - 标准: `SELECT tourney_name FROM matches GROUP BY tourney_name HAVING count(*)  >  10`
  - 预测: `SELECT T1.tourney_name FROM tournaments AS T1 JOIN matches AS T2 ON T1.tournament_id = T2.tournament_id GROUP BY T1.tournament_id HAVING count(*) > 10`
  - 原因: pred_error: no such table: tournaments

- 问题: Find the number of cartoons directed by each of the listed directors.
  - db: tvshow
  - 标准: `SELECT count(*) ,  Directed_by FROM cartoon GROUP BY Directed_by`
  - 预测: `SELECT count(*) , directed_by FROM CARTON GROUP BY directed_by`
  - 原因: pred_error: no such table: CARTON

- 问题: How long is the people’s average life expectancy in Central Africa?
  - db: world_1
  - 标准: `SELECT avg(LifeExpectancy) FROM country WHERE Region  =  "Central Africa"`
  - 预测: `SELECT avg(T1.LifeExpectancy) FROM country AS T1 JOIN continent AS T2 ON T1.Continent = T2.Name WHERE T2.Region = "Central Africa"`
  - 原因: pred_error: no such table: continent

- 问题: What is the name and country of origin of every singer who has a song with the word 'Hey' in its title?
  - db: concert_singer
  - 标准: `SELECT name ,  country FROM singer WHERE song_name LIKE '%Hey%'`
  - 预测: `SELECT T2.Name , T2.Country FROM song AS T1 JOIN singer AS T2 ON T1.Singer_ID = T2.Singer_ID WHERE T1.Title LIKE '%Hey%'`
  - 原因: pred_error: no such table: song

## 结果错误/缺少结构: nested（共 10 条）

- 问题: Find the average age of the dogs who went through treatments.
  - db: dog_kennels
  - 标准: `SELECT avg(age) FROM Dogs WHERE dog_id IN ( SELECT dog_id FROM Treatments )`
  - 预测: `SELECT avg(T1.age) FROM dogs AS T1 JOIN treatments AS T2 ON T1.dog_id = T2.dog_id`
  - 原因: wrong_result

- 问题: Who owns the youngest dog? Give me his or her last name.
  - db: dog_kennels
  - 标准: `SELECT T1.last_name FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id  =  T2.owner_id WHERE T2.age  =  ( SELECT max(age) FROM Dogs )`
  - 预测: `SELECT T1.last_name FROM owners AS T1 JOIN dogs AS T2 ON T1.owner_id = T2.owner_id ORDER BY T2.age LIMIT 1`
  - 原因: wrong_result

- 问题: What is the maker of the carr produced in the earliest year and what year was it?
  - db: car_1
  - 标准: `SELECT T2.Make ,  T1.Year FROM CARS_DATA AS T1 JOIN CAR_NAMES AS T2 ON T1.Id  =  T2.MakeId WHERE T1.Year  =  (SELECT min(YEAR) FROM CARS_DATA);`
  - 预测: `SELECT T2.Maker , T1.Year FROM cars_data AS T1 JOIN car_makers AS T2 ON T1.id = T2.id ORDER BY T1.year ASC LIMIT 1`
  - 原因: wrong_result

- 问题: How many people live in countries that do not speak English?
  - db: world_1
  - 标准: `SELECT sum(Population) FROM country WHERE Name NOT IN (SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "English")`
  - 预测: `SELECT sum(T1.population) FROM city AS T1 JOIN countrylanguage AS T2 ON T1.countrycode = T2.countrycode WHERE T2.language != 'English'`
  - 原因: wrong_result

- 问题: What is the average grade of students who have friends?
  - db: network_1
  - 标准: `SELECT avg(grade) FROM Highschooler WHERE id IN (SELECT T1.student_id FROM Friend AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id)`
  - 预测: `SELECT avg(T1.grade) FROM highschooler AS T1 JOIN friend AS T2 ON T1.id = T2.student_id`
  - 原因: wrong_result

- 问题: Find the average grade of all students who have some friends.
  - db: network_1
  - 标准: `SELECT avg(grade) FROM Highschooler WHERE id IN (SELECT T1.student_id FROM Friend AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id)`
  - 预测: `SELECT avg(T1.grade) FROM highschooler AS T1 JOIN friend AS T2 ON T1.id = T2.student_id`
  - 原因: wrong_result

- 问题: What is the average age of the dogs who have gone through any treatments?
  - db: dog_kennels
  - 标准: `SELECT avg(age) FROM Dogs WHERE dog_id IN ( SELECT dog_id FROM Treatments )`
  - 预测: `SELECT avg(T1.age) FROM dogs AS T1 JOIN treatments AS T2 ON T1.dog_id = T2.dog_id`
  - 原因: wrong_result

- 问题: What is the total number of people living in the nations that do not use English?
  - db: world_1
  - 标准: `SELECT sum(Population) FROM country WHERE Name NOT IN (SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "English")`
  - 预测: `SELECT sum(T1.Population) FROM city AS T1 JOIN countrylanguage AS T2 ON T1.CountryCode = T2.CountryCode WHERE T2.Language != 'English'`
  - 原因: wrong_result

- 问题: List the last name of the owner owning the youngest dog.
  - db: dog_kennels
  - 标准: `SELECT T1.last_name FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id  =  T2.owner_id WHERE T2.age  =  ( SELECT max(age) FROM Dogs )`
  - 预测: `SELECT T1.last_name FROM owners AS T1 JOIN dogs AS T2 ON T1.owner_id = T2.owner_id ORDER BY T2.age LIMIT 1`
  - 原因: wrong_result

- 问题: What are the names of the dogs for which the owner has not spend more than 1000 for treatment ?
  - db: dog_kennels
  - 标准: `select name from dogs where dog_id not in ( select dog_id from treatments group by dog_id having sum(cost_of_treatment)  >  1000 )`
  - 预测: `SELECT T2.name FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id = T2.owner_id JOIN Treatments AS T3 ON T2.dog_id = T3.dog_id GROUP BY T2.dog_id HAVING sum(T3.cost_of_treatment) > 1000`
  - 原因: wrong_result

## 执行报错/其他（共 9 条）

- 问题: Which professionals live in the state of Indiana or have done treatment on more than 2 treatments? List his or her id, last name and cell phone.
  - db: dog_kennels
  - 标准: `SELECT professional_id ,  last_name ,  cell_number FROM Professionals WHERE state  =  'Indiana' UNION SELECT T1.professional_id ,  T1.last_name ,  T1.cell_number FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id  =  T2.professional_id GROUP BY T1.professional_id HAVING count(*)  >  2`
  - 预测: `SELECT T1.professional_id , T1.last_name , T1.cell_number FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id = T2.professional_id WHERE T1.state = "Indiana" OR count(*) > 2`
  - 原因: pred_error: misuse of aggregate function count()

- 问题: Which dogs are of the rarest breed? Show their names and treatment dates.
  - db: dog_kennels
  - 标准: `SELECT T1.name ,  T2.date_of_treatment FROM Dogs AS T1 JOIN Treatments AS T2 ON T1.dog_id  =  T2.dog_id WHERE T1.breed_code  =  ( SELECT breed_code FROM Dogs GROUP BY breed_code ORDER BY count(*) ASC LIMIT 1 )`
  - 预测: `SELECT T1.name , T2.date_of_treatment FROM Dogs AS T1 JOIN Treatments AS T2 ON T1.dog_id = T2.dog_id WHERE T1.breed_code IN ( SELECT breed_code FROM Breeds ORDER BY count(*) ASC LIMIT 1 )`
  - 原因: pred_error: misuse of aggregate: count()

- 问题: What is the name and capacity for the stadium with highest average attendance?
  - db: concert_singer
  - 标准: `SELECT name ,  capacity FROM stadium ORDER BY average DESC LIMIT 1`
  - 预测: `SELECT name , capacity FROM stadium ORDER BY avg(Highest) DESC LIMIT 1`
  - 原因: pred_error: misuse of aggregate: avg()

- 问题: What are the ids and makers of all car makers that produce at least 2 models and make more than 3 cars?
  - db: car_1
  - 标准: `SELECT T1.Id ,  T1.Maker FROM CAR_MAKERS AS T1 JOIN MODEL_LIST AS T2 ON T1.Id  =  T2.Maker GROUP BY T1.Id HAVING count(*)  >=  2 INTERSECT SELECT T1.Id ,  T1.Maker FROM CAR_MAKERS AS T1 JOIN MODEL_LIST AS T2 ON T1.Id  =  T2.Maker JOIN CAR_NAMES AS T3 ON T2.model  =  T3.model GROUP BY T1.Id HAVING count(*)  >  3;`
  - 预测: `SELECT id , maker FROM car_makers WHERE count(*) >= 2 AND count(*) > 3`
  - 原因: pred_error: misuse of aggregate function count()

- 问题: What is the total population and maximum GNP in Asia?
  - db: world_1
  - 标准: `SELECT sum(Population) ,  max(GNP) FROM country WHERE Continent  =  "Asia"`
  - 预测: `SELECT sum(max(T1.Population)) , max(T2.GNP) FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code = T2.CountryCode WHERE T1.Continent = 'Asia'`
  - 原因: pred_error: misuse of aggregate function max()

- 问题: Find the first name, country code and birth date of the winner who has the highest rank points in all matches.
  - db: wta_1
  - 标准: `SELECT T1.first_name ,  T1.country_code ,  T1.birth_date FROM players AS T1 JOIN matches AS T2 ON T1.player_id  =  T2.winner_id ORDER BY T2.winner_rank_points DESC LIMIT 1`
  - 预测: `SELECT T1.first_name , T1.country_code , T1.birth_date FROM players AS T1 JOIN MATCHES AS T2 ON T1.player_id = T2.winner_rank_points = ( SELECT max(T2.winner_rank_points) FROM matches )`
  - 原因: pred_error: misuse of aggregate: max()

- 问题: What is the name and capacity for the stadium with the highest average attendance?
  - db: concert_singer
  - 标准: `SELECT name ,  capacity FROM stadium ORDER BY average DESC LIMIT 1`
  - 预测: `SELECT name , capacity FROM stadium ORDER BY avg(Highest) DESC LIMIT 1`
  - 原因: pred_error: misuse of aggregate: avg()

- 问题: What is the total number of unique official languages spoken in the countries that are founded before 1930?
  - db: world_1
  - 标准: `SELECT count(DISTINCT T2.Language) FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE  IndepYear  <  1930 AND T2.IsOfficial  =  "T"`
  - 预测: `SELECT sum(count(DISTINCT T1.Language)) FROM countrylanguage AS T1 JOIN country AS T2 ON T1.CountryCode = T2.Code WHERE T2.IndepYear < 1930`
  - 原因: pred_error: misuse of aggregate function count()

- 问题: Find the id, last name and cell phone of the professionals who live in the state of Indiana or have performed more than two treatments.
  - db: dog_kennels
  - 标准: `SELECT professional_id ,  last_name ,  cell_number FROM Professionals WHERE state  =  'Indiana' UNION SELECT T1.professional_id ,  T1.last_name ,  T1.cell_number FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id  =  T2.professional_id GROUP BY T1.professional_id HAVING count(*)  >  2`
  - 预测: `SELECT T1.professional_id , T1.last_name , T1.cell_number FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id = T2.professional_id WHERE T1.state = "Indiana" OR COUNT(*) > 2`
  - 原因: pred_error: misuse of aggregate function COUNT()

## 结果错误/缺少结构: join（共 9 条）

- 问题: How many official languages are spoken in Afghanistan?
  - db: world_1
  - 标准: `SELECT COUNT(*) FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T1.Name  =  "Afghanistan" AND IsOfficial  =  "T"`
  - 预测: `SELECT count(*) FROM countrylanguage WHERE countrycode = 'AF'`
  - 原因: wrong_result

- 问题: What is the number of nations that use English and Dutch?
  - db: world_1
  - 标准: `SELECT COUNT(*) FROM (SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "English" INTERSECT SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "Dutch")`
  - 预测: `SELECT count(*) FROM countrylanguage WHERE Language = "English" INTERSECT SELECT count(*) FROM countrylanguage WHERE Language = "Dutch"`
  - 原因: wrong_result

- 问题: What are the codes of template types that are not used for any document?
  - db: cre_Doc_Template_Mgt
  - 标准: `SELECT template_type_code FROM Templates EXCEPT SELECT template_type_code FROM Templates AS T1 JOIN Documents AS T2 ON T1.template_id  =  T2.template_id`
  - 预测: `SELECT template_type_code FROM Ref_template_types EXCEPT SELECT template_type_code FROM Templates`
  - 原因: wrong_result

- 问题: Which region is the city Kabul located in?
  - db: world_1
  - 标准: `SELECT Region FROM country AS T1 JOIN city AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Name  =  "Kabul"`
  - 预测: `SELECT district FROM city WHERE name = "Kabul"`
  - 原因: wrong_result

- 问题: How many languages are spoken in Aruba?
  - db: world_1
  - 标准: `SELECT COUNT(T2.Language) FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T1.Name  =  "Aruba"`
  - 预测: `SELECT count(*) FROM countrylanguage WHERE CountryCode = "AW"`
  - 原因: wrong_result

- 问题: What region is Kabul in?
  - db: world_1
  - 标准: `SELECT Region FROM country AS T1 JOIN city AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Name  =  "Kabul"`
  - 预测: `SELECT REGION FROM country WHERE CAPITAL = 'Kabul'`
  - 原因: wrong_result

- 问题: What is the id of the semester that had both Masters and Bachelors students enrolled?
  - db: student_transcripts_tracking
  - 标准: `SELECT DISTINCT T2.semester_id FROM Degree_Programs AS T1 JOIN Student_Enrolment AS T2 ON T1.degree_program_id  =  T2.degree_program_id WHERE degree_summary_name  =  'Master' INTERSECT SELECT DISTINCT T2.semester_id FROM Degree_Programs AS T1 JOIN Student_Enrolment AS T2 ON T1.degree_program_id  =  T2.degree_program_id WHERE degree_summary_name  =  'Bachelor'`
  - 预测: `SELECT semester_id FROM Student_Enrolment WHERE degree_program_id = 'MA' INTERSECT SELECT semester_id FROM Student_Enrolment WHERE degree_program_id = 'BA'`
  - 原因: wrong_result

- 问题: How many official languages does Afghanistan have?
  - db: world_1
  - 标准: `SELECT COUNT(*) FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T1.Name  =  "Afghanistan" AND IsOfficial  =  "T"`
  - 预测: `SELECT count(*) FROM countrylanguage WHERE countrycode = 'AF'`
  - 原因: wrong_result

- 问题: How many countries speak both English and Dutch?
  - db: world_1
  - 标准: `SELECT COUNT(*) FROM (SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "English" INTERSECT SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "Dutch")`
  - 预测: `SELECT count(*) FROM countrylanguage WHERE Language = "English" INTERSECT SELECT count(*) FROM countrylanguage WHERE Language = "Dutch"`
  - 原因: wrong_result

## 结果错误/缺少结构: order_by（共 4 条）

- 问题: What language is predominantly spoken in Aruba?
  - db: world_1
  - 标准: `SELECT T2.Language FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T1.Name  =  "Aruba" ORDER BY Percentage DESC LIMIT 1`
  - 预测: `SELECT T1.language FROM countrylanguage AS T1 JOIN city AS T2 ON T1.countrycode = T2.countrycode WHERE T2.name = "Aruba"`
  - 原因: wrong_result

- 问题: How many cars have a larger accelerate than the car with the largest horsepower?
  - db: car_1
  - 标准: `SELECT COUNT(*) FROM CARS_DATA WHERE Accelerate  >  ( SELECT Accelerate FROM CARS_DATA ORDER BY Horsepower DESC LIMIT 1 );`
  - 预测: `SELECT count(*) FROM cars_data WHERE Accelerate > (SELECT max(Accelerate) FROM cars_data )`
  - 原因: wrong_result

- 问题: Show the stadium name and capacity with most number of concerts in year 2014 or after.
  - db: concert_singer
  - 标准: `SELECT T2.name ,  T2.capacity FROM concert AS T1 JOIN stadium AS T2 ON T1.stadium_id  =  T2.stadium_id WHERE T1.year  >=  2014 GROUP BY T2.stadium_id ORDER BY count(*) DESC LIMIT 1`
  - 预测: `SELECT T2.name , T2.capacity FROM concert AS T1 JOIN stadium AS T2 ON T1.stadium_id = T2.stadium_id WHERE T1.year >= 2014 GROUP BY T1.stadium_id HAVING count(*) > 5`
  - 原因: wrong_result

- 问题: What is the number of cars with a greater accelerate than the one with the most horsepower?
  - db: car_1
  - 标准: `SELECT COUNT(*) FROM CARS_DATA WHERE Accelerate  >  ( SELECT Accelerate FROM CARS_DATA ORDER BY Horsepower DESC LIMIT 1 );`
  - 预测: `SELECT count(*) FROM cars_data WHERE Accelerate > (SELECT max(Accelerate) FROM cars_data)`
  - 原因: wrong_result

## 结果错误/缺少结构: group_by（共 4 条）

- 问题: What are the codes of countries where Spanish is spoken by the largest percentage of people?
  - db: world_1
  - 标准: `SELECT CountryCode ,  max(Percentage) FROM countrylanguage WHERE LANGUAGE  =  "Spanish" GROUP BY CountryCode`
  - 预测: `SELECT CountryCode FROM countrylanguage WHERE Language = "Spanish" AND Percentage = (SELECT max(Percentage) FROM countrylanguage WHERE Language = "Spanish")`
  - 原因: wrong_result

- 问题: What is the language spoken by the largest percentage of people in each country?
  - db: world_1
  - 标准: `SELECT LANGUAGE ,  CountryCode ,  max(Percentage) FROM countrylanguage GROUP BY CountryCode`
  - 预测: `SELECT T1.Language , T2.Name FROM countrylanguage AS T1 JOIN country AS T2 ON T1.CountryCode = T2.Code ORDER BY T1.Percentage DESC LIMIT 1`
  - 原因: wrong_result

- 问题: What are the names and ids of all countries with at least one car maker?
  - db: car_1
  - 标准: `SELECT T1.CountryName ,  T1.CountryId FROM COUNTRIES AS T1 JOIN CAR_MAKERS AS T2 ON T1.CountryId  =  T2.Country GROUP BY T1.CountryId HAVING count(*)  >=  1;`
  - 预测: `SELECT T1.CountryName , T2.id FROM countries AS T1 JOIN car_makers AS T2 ON T1.CountryId = T2.Country`
  - 原因: wrong_result

- 问题: Count the number of countries for which Spanish is the predominantly spoken language.
  - db: world_1
  - 标准: `SELECT count(*) ,   max(Percentage) FROM countrylanguage WHERE LANGUAGE  =  "Spanish" GROUP BY CountryCode`
  - 预测: `SELECT count(*) FROM countrylanguage WHERE Language = "Spanish" AND IsOfficial = "Yes"`
  - 原因: wrong_result

## 执行报错/语法错误（共 4 条）

- 问题: Find the average life expectancy and total population for each continent where the average life expectancy is shorter than 72?
  - db: world_1
  - 标准: `SELECT sum(Population) ,  avg(LifeExpectancy) ,  Continent FROM country GROUP BY Continent HAVING avg(LifeExpectancy)  <  72`
  - 预测: `SELECT avg(LE) , sum(population) , continent FROM city GROUP BY continent WHERE avg(LE) < 72`
  - 原因: pred_error: near "WHERE": syntax error

- 问题: What are the names of all European countries with at least 3 manufacturers?
  - db: car_1
  - 标准: `SELECT T1.CountryName FROM COUNTRIES AS T1 JOIN CONTINENTS AS T2 ON T1.Continent  =  T2.ContId JOIN CAR_MAKERS AS T3 ON T1.CountryId  =  T3.Country WHERE T2.Continent  =  'europe' GROUP BY T1.CountryName HAVING count(*)  >=  3;`
  - 预测: `SELECT T1.CountryName FROM countries AS T1 JOIN car_makers AS T2 ON T1.CountryId = T2.Country GROUP BY T1.CountryName HAVING T1.Continent = "Europe" COUNT(*) >= 3`
  - 原因: pred_error: near "COUNT": syntax error

- 问题: Which countries in europe have at least 3 car manufacturers?
  - db: car_1
  - 标准: `SELECT T1.CountryName FROM COUNTRIES AS T1 JOIN CONTINENTS AS T2 ON T1.Continent  =  T2.ContId JOIN CAR_MAKERS AS T3 ON T1.CountryId  =  T3.Country WHERE T2.Continent  =  'europe' GROUP BY T1.CountryName HAVING count(*)  >=  3;`
  - 预测: `SELECT T1.CountryName FROM countries AS T1 JOIN car_makers AS T2 ON T1.CountryId = T2.Country GROUP BY T1.CountryName HAVING T1.Continent = "Europe" COUNT(*) >= 3`
  - 原因: pred_error: near "COUNT": syntax error

- 问题: What is the first name of the student whose permanent address is different from his or her current one?
  - db: student_transcripts_tracking
  - 标准: `SELECT first_name FROM Students WHERE current_address_id != permanent_address_id`
  - 预测: `SELECT T1.first_name FROM students AS T1 JOIN addresses AS T2 ON T1.permanent_address_id = T2.address_id WHERE T2.line_1 != T2.line_1 FROM addresses AS T2 ON T1.current_address_id = T2.address_id`
  - 原因: pred_error: near "FROM": syntax error

## 结果错误/用集合操作代替了子查询（写法不同，结果也不同）（共 3 条）

- 问题: find the package option of the tv channel that do not have any cartoon directed by Ben Jones.
  - db: tvshow
  - 标准: `SELECT package_option FROM TV_Channel WHERE id NOT IN (SELECT channel FROM cartoon WHERE directed_by  =  'Ben Jones')`
  - 预测: `SELECT package_option FROM TV_channel EXCEPT SELECT T1.package_option FROM TV_channel AS T1 JOIN Cartoon AS T2 ON T1.id = T2.channel WHERE T2.directed_by = "Ben Jones"`
  - 原因: wrong_result

- 问题: What are the package options of all tv channels that are not playing any cartoons directed by Ben Jones?
  - db: tvshow
  - 标准: `SELECT package_option FROM TV_Channel WHERE id NOT IN (SELECT channel FROM cartoon WHERE directed_by  =  'Ben Jones')`
  - 预测: `SELECT package_option FROM TV_channel EXCEPT SELECT T2.package_option FROM Cartoon AS T1 JOIN TV_channel AS T2 ON T1.channel = T2.id WHERE T1.directed_by = "Ben Jones"`
  - 原因: wrong_result

- 问题: What is the first name of every student who has a dog but does not have a cat?
  - db: pets_1
  - 标准: `SELECT T1.fname ,  T1.age FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid  =  T2.stuid JOIN pets AS T3 ON T3.petid  =  T2.petid WHERE T3.pettype  =  'dog' AND T1.stuid NOT IN (SELECT T1.stuid FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid  =  T2.stuid JOIN pets AS T3 ON T3.petid  =  T2.petid WHERE T3.pettype  =  'cat')`
  - 预测: `SELECT T1.Fname FROM Student AS T1 JOIN Has_Pet AS T2 ON T1.StuID = T2.StuID JOIN Pets AS T3 ON T2.PetID = T3.PetID WHERE T3.PetType = "dog" EXCEPT SELECT T1.Fname FROM Student AS T1 JOIN Has_Pet AS T2 ON T1.StuID = T2.StuID JOIN Pets AS T3 ON T2.PetID = T3.PetID WHERE T3.PetType = "cat"`
  - 原因: wrong_result

## 执行报错/列名有歧义（共 3 条）

- 问题: Show all document ids, names and the number of paragraphs in each document.
  - db: cre_Doc_Template_Mgt
  - 标准: `SELECT T1.document_id ,  T2.document_name ,  count(*) FROM Paragraphs AS T1 JOIN Documents AS T2 ON T1.document_id  =  T2.document_id GROUP BY T1.document_id`
  - 预测: `SELECT document_id , document_name , count(*) FROM Documents AS T1 JOIN Paragraphs AS T2 ON T1.document_id = T2.document_id GROUP BY document_id`
  - 原因: pred_error: ambiguous column name: document_id

- 问题: What are the package options and the name of the series for the TV Channel that supports high definition TV?
  - db: tvshow
  - 标准: `SELECT package_option ,  series_name FROM TV_Channel WHERE hight_definition_TV  =  "yes"`
  - 预测: `SELECT Package_Option , T2.series_name FROM TV_channel AS T1 JOIN TV_channel AS T2 ON T1.id = T2.package_option WHERE T1.Hight_definition_TV = 'Yes'`
  - 原因: pred_error: ambiguous column name: Package_Option

- 问题: What are the different models wthat are lighter than 3500 but were not built by the Ford Motor Company?
  - db: car_1
  - 标准: `SELECT DISTINCT T1.model FROM MODEL_LIST AS T1 JOIN CAR_NAMES AS T2 ON T1.Model  =  T2.Model JOIN CARS_DATA AS T3 ON T2.MakeId  =  T3.Id JOIN CAR_MAKERS AS T4 ON T1.Maker  =  T4.Id WHERE T3.weight  <  3500 AND T4.FullName != 'Ford Motor Company';`
  - 预测: `SELECT DISTINCT model FROM model_list WHERE weight < 3500 EXCEPT SELECT DISTINCT model FROM car_makers JOIN model_list ON car_makers.id = model_list.maker JOIN car_names ON model_list.model = car_names.model WHERE car_makers.fullname = 'Ford'`
  - 原因: pred_error: ambiguous column name: model

## 结果错误/缺少结构: set_op（共 3 条）

- 问题: What are the countries where either English or Dutch is the official language ?
  - db: world_1
  - 标准: `select t1.name from country as t1 join countrylanguage as t2 on t1.code  =  t2.countrycode where t2.language  =  "english" and isofficial  =  "t" union select t1.name from country as t1 join countrylanguage as t2 on t1.code  =  t2.countrycode where t2.language  =  "dutch" and isofficial  =  "t"`
  - 预测: `SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code = T2.CountryCode WHERE T2.Language = "English" OR T2.Language = "Dutch"`
  - 原因: wrong_result

- 问题: Which countries have either English or Dutch as an official language?
  - db: world_1
  - 标准: `SELECT * FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "English" AND IsOfficial  =  "T" UNION SELECT * FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "Dutch" AND IsOfficial  =  "T"`
  - 预测: `SELECT T1.name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.code = T2.countrycode WHERE T2.language = "English" OR T2.language = "Dutch"`
  - 原因: wrong_result

- 问题: What are the ids of documents that contain the paragraph text 'Brazil' and 'Ireland'?
  - db: cre_Doc_Template_Mgt
  - 标准: `SELECT document_id FROM Paragraphs WHERE paragraph_text  =  'Brazil' INTERSECT SELECT document_id FROM Paragraphs WHERE paragraph_text  =  'Ireland'`
  - 预测: `SELECT T1.document_id FROM Documents AS T1 JOIN Paragraphs AS T2 ON T1.document_id = T2.document_id WHERE T2.paragraph_text LIKE '%Brazil%' AND T2.paragraph_text LIKE '%Ireland%'`
  - 原因: wrong_result

## 结果错误/缺少结构: group_by,nested（共 1 条）

- 问题: Which dogs have not cost their owner more than 1000 for treatment ? List the dog names .
  - db: dog_kennels
  - 标准: `select name from dogs where dog_id not in ( select dog_id from treatments group by dog_id having sum(cost_of_treatment)  >  1000 )`
  - 预测: `SELECT T2.name FROM treatments AS T1 JOIN dogs AS T2 ON T1.dog_id = T2.dog_id WHERE T1.cost_of_treatment < 1000`
  - 原因: wrong_result

