from django.core.files.base import File
from django.shortcuts import render
from .forms import UploadFileForm
from django.views.decorators.csrf import ensure_csrf_cookie
import os
from .helpers import JointDetection
from .helpers import Model
from .helpers.PoseTimeSeries.PoseTimeSeries import PoseTimeSeries
from .models import FormCheck, PoseTimeSeries as PoseTimeSeriesModel
from django.shortcuts import redirect
import json


@ensure_csrf_cookie
def squat_form_check(request):
    if not request.user.is_authenticated:
        form = UploadFileForm()
        return render(request, 'upload-display-video.html', {'form': form})

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            handle_uploaded_file(file)
            squat_video_data = JointDetection.readFromJSONFile()
            joints, angles = JointDetection.getJointsAnglesForVideo(file.name, generateVideo=True)
            input_series = PoseTimeSeries(joints, angles)

            nearest = Model.knearest(input_series, squat_video_data)
            depth_check = Model.checkDepth(input_series)
            additional_feedback = None
            if(len(depth_check) > 0):
                additional_feedback = ":".join(depth_check)

            form_check = FormCheck(user=request.user, prediction=nearest[0].label, additional_feedback=additional_feedback)

            nearest_PoseTimeSeries1 = PoseTimeSeriesModel.objects.filter(name=nearest[0].name)
            if nearest_PoseTimeSeries1.exists():
                form_check.nearest1 = nearest_PoseTimeSeries1.first()
            nearest_PoseTimeSeries2 = PoseTimeSeriesModel.objects.filter(name=nearest[1].name)
            if nearest_PoseTimeSeries2.exists():
                form_check.nearest2 = nearest_PoseTimeSeries2.first()
            nearest_PoseTimeSeries3 = PoseTimeSeriesModel.objects.filter(name=nearest[2].name)
            if nearest_PoseTimeSeries3.exists():
                form_check.nearest3 = nearest_PoseTimeSeries3.first()

            skeleton_file_name = file.name[0:len(file.name)-4] + '_skeleton.webm'
            with open(skeleton_file_name, "rb") as f:
                form_check.skeleton_video.save(skeleton_file_name, File(f))
            form_check.save()

            return render(request, "upload-display-video.html", {"form_check": form_check})
    else:
        form = UploadFileForm()
    return render(request, 'upload-display-video.html', {'form': form})

def handle_uploaded_file(f):
    with open(f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def history(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            formchecks = FormCheck.objects.filter(user=request.user)
            return render(request, 'history.html', {'form_checks': formchecks})

# adds all our training data onto database. Including feedback.
def script(request):
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    #all = JointDetection.trainAllVideos(absolute_path + '/helpers')
    #JointDetection.writeToJSONFile(all, absolute_path + '/helpers')
    file_path = absolute_path + "/helpers/train.json"
    with open(file_path, "r") as f:
        data = json.load(f)
    for item in data:
        feedback = ""
        if item["feedback"][0]:
            feedback = ":".join(item["feedback"])
        series = PoseTimeSeriesModel(name=item["name"], label=item["label"], feedback=feedback)
        video_name = absolute_path + '/helpers/videos/' + item["name"]
        with open(video_name, "rb") as f:
            series.original_video.save(item["name"], File(f))
        series.save()

    return redirect(squat_form_check)
