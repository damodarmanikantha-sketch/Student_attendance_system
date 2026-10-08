from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import AttendanceForm,FaceVerificationForm
from .models import Attendance
from django.core.mail import send_mail
from django.conf import settings


from .face_utils import verify_face
@login_required
def submit_attendance(request):
    if request.user.role != "STUDENT":
        return redirect("home")

    today = timezone.localdate()

    if Attendance.objects.filter(
        student=request.user,
        attendance_date=today
    ).exists():
        return render(
            request,
            "attendance/submit_attendance.html",
            {"error": "You have already submitted attendance today."}
        )

    if request.method == "POST":
        form = AttendanceForm(request.POST)
        image = request.FILES.get("face_image")

        if not image:
            return render(
                request,
                "attendance/submit_attendance.html",
                {"form": form, "error": "Please capture your face."}
            )
            
        import os

        print("Face Image:", request.user.face_image)
        print("Reference Path:", request.user.face_image.path)

        print("Exists:", os.path.exists(request.user.face_image.path))

        reference = request.user.face_image.path

        if form.is_valid() and verify_face(image, reference):
            attendance = form.save(commit=False)
            attendance.student = request.user
            attendance.attendance_date = today
            attendance.status = "PENDING"
            attendance.save()

            return redirect("attendance_success")

        return render(
            request,
            "attendance/submit_attendance.html",
            {"form": form, "error": "Face verification failed."}
        )

    return render(
        request,
        "attendance/submit_attendance.html",
        {"form": AttendanceForm()}
    )


@login_required
def attendance_success(request):
    return render(request,"attendance/attendance_success.html")
@login_required
def attendance_history(request):

    if request.user.role != "STUDENT":
        return redirect("home")
    
    records = Attendance.objects.filter(student=request.user)

    return render(request,"attendance/attendance_history.html",{"records": records},)



# Show pending attendance and summary
@login_required
def attendance_approvals(request):
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        return redirect("home")

    pending = Attendance.objects.filter(status="PENDING")

    summary = {
        "pending": pending.count(),
        "approved": Attendance.objects.filter(status="APPROVED").count(),
        "rejected": Attendance.objects.filter(status="REJECTED").count(),
    }

    return render(request, "attendance/attendance_approvals.html", {
        "pending_records": pending,
        "summary": summary,
    })

# Approve selected attendance
@login_required
def approve_attendance(request, attendance_id):
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        return redirect("home")

    if request.method == "POST":
        attendance = Attendance.objects.filter(id=attendance_id,status="PENDING").first()

        if attendance:
            attendance.status = "APPROVED"
            attendance.save()

            send_mail(
                "Attendance Approved",
                f"Your attendance for {attendance.attendance_date} has been approved.",
                settings.DEFAULT_FROM_EMAIL,
                [attendance.student.email],
            )

    return redirect("attendance_approvals")