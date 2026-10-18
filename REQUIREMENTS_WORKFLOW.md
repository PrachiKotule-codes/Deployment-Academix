# ACADEMIX role-wise requirements and workflow

This document consolidates the two workbook requirements into the workflows used by this project. The shared visual shell may be common, but each role has its own dashboard, navigation and server-side access rules.

## 1. Admin / institution administration

**Purpose:** maintain the institution setup and oversee academic records.

- Create accounts, assign roles and student class/division.
- Link each parent to the correct student account.
- View all courses, teachers, students and parents.
- Review attendance and homework activity.
- Create fee records and record fee payments.
- View institution-level academic reports and notifications.

**Workflow:** Admin creates or updates accounts and assignments → teachers create courses and learning activity → Admin monitors records and reports. Student and parent records are scoped by role and links rather than by navigation alone.

## 2. Teacher

**Purpose:** create and deliver lessons, evaluate student work and manage assigned class activity.

- Create/edit owned courses with subject, module, class, division and publication status.
- Add/edit ordered lessons, video URL/file, study materials, quick recap and mindmap link.
- Publish course and lesson content so enrolled/class-matched students can access it.
- Create homework with instructions and due date; review submissions and enter marks/feedback.
- View students in classes associated with owned courses.
- Mark Present / Absent / Late / Leave attendance for permitted students and date.
- Maintain timetable entries linked to the teacher's course/class assignment.
- View reports from their own homework/test activity.

**Workflow:** create course → add lessons and learning materials → publish → assign/create homework → receive submissions → review and feedback → mark attendance → view performance.

## 3. Student

**Purpose:** access published learning materials and personal academic records.

- Sign in or register an account; class/division can be supplied at signup or assigned by Admin.
- Browse published courses for the student's class/division.
- Watch linked/uploaded lesson video, open uploaded/external study materials, open mindmap links and read quick recaps.
- Mark lessons completed and view course completion progress.
- View published homework, submit written work or an attachment, and read review marks/feedback.
- View personal attendance, timetable, fee balance, results and notifications.

**Workflow:** sign in → open assigned published course → study lessons and materials → mark progress → submit homework → review teacher feedback → check attendance/results/fees.

## 4. Parent

**Purpose:** monitor the linked child's learning and school records.

- Sign in/register; Admin must link the Parent account to the correct Student account.
- View linked child's published courses and progress summaries.
- View the linked child's homework and whether each assignment is not submitted, submitted or reviewed.
- View linked-child attendance, timetable, fees, results and notifications.
- Receive in-app alerts for absence, new homework, homework review and fee records/payment changes.

**Workflow:** Admin links parent to child → parent signs in → reviews linked-child progress and activity → follows notifications and checks outstanding work/fees. A parent with no linked child is shown a clear message instead of other students' records.

## 5. Cross-module data flow

1. A course belongs to a subject, teacher, class/division and academic year.
2. Lessons and study materials belong to the course/lesson.
3. Students see only published courses/lessons matched to their class/division.
4. Homework belongs to a course; student submissions link the homework to the submitting student; teachers save review marks and feedback.
5. Attendance is stored by student and date, with the last status for that student/date updated on re-marking.
6. Fees belong to a student; payments belong to a fee record; a printable receipt is available for saved payment records.
7. Reports aggregate recorded submissions and test attempts. In-app notifications go to relevant student and linked parent accounts.

## 6. Demo accounts

| Role | Username | Password |
|---|---|---|
| Admin | `admin_demo` | `Admin123` |
| Teacher | `teacher_demo` | `Teacher123` |
| Student | `student_demo` | `Student123` |
| Parent | `parent_demo` | `Parent123` |

The seed command also creates `teacher2`–`teacher5`, `student2`–`student10` and `parent2`–`parent10`. Demo passwords are reset each time `python manage.py seed_demo` is run. Local-demo accounts must not be deployed or used with real student data.

## 7. Submission verification checklist

After the local PostgreSQL setup succeeds, verify in this order:

1. Log in with each role and confirm that the dashboard and sidebar are different.
2. As `teacher_demo`, open Course Management, create a course, add a lesson, attach study material, and publish it.
3. As `student_demo`, open the published course, open a lesson, mark it complete, then submit the sample homework.
4. As `teacher_demo`, review the homework and save marks/feedback.
5. As `teacher_demo`, mark attendance for a selected date; as `student_demo` and `parent_demo`, verify the relevant records/notifications.
6. As `admin_demo`, verify the account list, parent-child link, fee record/payment, receipt, and CSV reports.

## 8. Explicit MVP boundaries

This is a submission-oriented MVP. It implements the primary role dashboards and core course/lesson/homework/attendance/timetable/fee/report paths, but the following are not complete production-grade workflows: timed exams with question authoring and automatic scoring, payment-gateway processing, full announcement create/edit/delete interface, full leave-request approval workflow, email password reset, PDF report generation, hardened file-upload controls, production deployment/security hardening and any claims of AI-based grading/generation. CSV result export and browser print-to-PDF for a fee receipt are provided; a real payment gateway is not.
