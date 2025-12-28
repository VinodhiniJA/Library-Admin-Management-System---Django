from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone

from .models import Book, Student, Issue


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('library:dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


@login_required(login_url='library:login')
def dashboard_view(request):
    total_books = Book.objects.count()
    total_students = Student.objects.count()
    issued_books = Issue.objects.filter(returned=False).count()
    returned_books = Issue.objects.filter(returned=True).count()

    return render(request, 'dashboard.html', {
        'total_books': total_books,
        'total_students': total_students,
        'issued_books': issued_books,
        'returned_books': returned_books,
    })



@login_required(login_url='library:login')
def logout_view(request):
    logout(request)
    return redirect('library:login')


@login_required(login_url='library:login')
def book_list(request):
    query = request.GET.get('q')

    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )
    else:
        books = Book.objects.all()

    return render(request, 'books.html', {'books': books})


@login_required(login_url='library:login')
def add_book(request):
    if request.method == 'POST':
        Book.objects.create(
            title=request.POST.get('title'),
            author=request.POST.get('author'),
            isbn=request.POST.get('isbn'),
            quantity=request.POST.get('quantity')
        )
        return redirect('library:books')

    return render(request, 'add_book.html')


@login_required(login_url='library:login')
def edit_book(request, id):
    book = get_object_or_404(Book, id=id)

    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.isbn = request.POST.get('isbn')
        book.quantity = request.POST.get('quantity')
        book.save()
        return redirect('library:books')

    return render(request, 'edit_book.html', {'book': book})


@login_required(login_url='library:login')
def delete_book(request, id):
    book = get_object_or_404(Book, id=id)
    book.delete()
    return redirect('library:books')


@login_required(login_url='library:login')
def student_list(request):
    q = request.GET.get('q')

    if q:
        students = Student.objects.filter(
            Q(name__icontains=q) |
            Q(roll_no__icontains=q) |
            Q(department__icontains=q)
        )
    else:
        students = Student.objects.all()

    return render(request, 'students.html', {
        'students': students
    })


@login_required(login_url='library:login')
def add_student(request):
    if request.method == 'POST':

        if not all([
            request.POST.get("name"),
            request.POST.get("roll_no"),
            request.POST.get("department"),
            request.POST.get("email"),
            request.POST.get("phone")
        ]):
            messages.error(request, "All fields are required")
            return redirect('library:add_student')  # 🔥 REDIRECT, NOT RENDER

        Student.objects.create(
            name=request.POST.get('name'),
            roll_no=request.POST.get('roll_no'),
            department=request.POST.get('department'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone')
        )

        messages.success(request, "Student added successfully")
        return redirect('library:students')

    return render(request, 'add_student.html')


@login_required(login_url='library:login')
def edit_student(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        student.name = request.POST.get('name')
        student.roll_no = request.POST.get('roll_no')
        student.department = request.POST.get('department')
        student.email = request.POST.get('email')
        student.phone = request.POST.get('phone')
        student.save()
        return redirect('library:students')

    return render(request, 'edit_student.html', {'student': student})


@login_required(login_url='library:login')
def delete_student(request, id):
    student = get_object_or_404(Student, id=id)
    student.delete()
    return redirect('library:students')


@login_required(login_url='library:login')
def issue_list(request):
    q = request.GET.get('q')

    if q:
        issues = Issue.objects.filter(
            student__name__icontains=q
        )
    else:
        issues = Issue.objects.all()

    return render(request, 'issues.html', {'issues': issues})


@login_required(login_url='login')
def issue_book(request):
    students = Student.objects.all()
    books = Book.objects.filter(quantity__gt=0)

    if request.method == 'POST':
        student_id = request.POST.get('student')
        book_id = request.POST.get('book')

        student = get_object_or_404(Student, id=student_id)
        book = get_object_or_404(Book, id=book_id)

        if book.quantity > 0:
            Issue.objects.create(
                student=student,
                book=book,
                issue_date=timezone.now()
            )

            book.quantity -= 1
            book.save()

            return redirect('library:issues')
        else:
            messages.error(request, 'Book not available')

    return render(request, 'issue_book.html', {
        'students': students,
        'books': books
    })


@login_required(login_url='library:login')
def return_book(request, id):
    issue = get_object_or_404(Issue, id=id)

    if not issue.returned:
        issue.returned = True
        issue.return_date = timezone.now().date()
        issue.save()

        issue.book.quantity += 1
        issue.book.save()

    return redirect('library:issues')

