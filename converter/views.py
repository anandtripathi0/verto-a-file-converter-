from django.shortcuts import render
from django.http import HttpResponse,FileResponse
from django.core.files.storage import FileSystemStorage
from PIL import Image
from docx import Document
from pdf2docx import Converter  
from dotenv import load_dotenv
import tempfile
import convertapi
import os
import fitz # pymupdf library 
import io

load_dotenv()

def main(request):
    return render(request,'index.html')

def img_to_pdf(request):
    if request.method=='POST':
        uploaded_image = request.FILES.getlist('images')
        if uploaded_image:
            img_list=[]

            for img in uploaded_image:
                opened_image = Image.open(img)
                converted_img = opened_image.convert('RGB')
                img_list.append(converted_img)

            if img_list:
                first_image = img_list[0]
                another_img = img_list[1:]

                pdf_buffer = io.BytesIO()

                first_image.save(
                    pdf_buffer,
                    format='PDF',
                    save_all = True,
                    append_images = another_img
                )

                pdf_buffer.seek(0)

                return FileResponse(pdf_buffer,as_attachment=True,filename='converted_doc.pdf')
        
    return render(request,'image_to_pdf.html')

def compress(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf_file')
        compression_level = request.POST.get('compression_level')

        if pdf_file:
            try:
                file_bytes = pdf_file.read()
                doc = fitz.open(stream=file_bytes,filetype='pdf')

                if compression_level == 'extreme':
                    garbage = 4
                    deflate = True

                elif compression_level == 'recommended':
                    garbage = 3
                    deflate = True

                else:
                    garbage = 1
                    deflate = True

                output_buffer = io.BytesIO()
                doc.save(output_buffer,garbage=garbage,deflate=deflate)
                doc.close()

                output_buffer.seek(0)

                return FileResponse(output_buffer,as_attachment=True,filename='compressed_doc.pdf')
            
            except Exception as e:
                print(f"error compressing PDF :{e}")
                return HttpResponse('Error compressing the file ',status = 500)
        else:
            return HttpResponse('No pdf file was uploaded',status = 400)
            
    return render(request,'compress.html')

def resizer(request):
   

    if request.method == 'POST':
        upload_file = request.FILES.get('upload_file')

        try:
            width = int(request.POST.get('width'))
            height = int(request.POST.get('height'))
        except ValueError:
            HttpResponse('invalid input',status=400)

        if upload_file:
            if upload_file.name.lower().endswith(('png','jpg','jpeg','webp')):
                try:
                    img=Image.open(upload_file)
                    resized_img  = img.resize((width,height),Image.Resampling.LANCZOS)
                    output_buffer = io.BytesIO()

                    image_format = img.format if img.format else 'JPEG'
                    resized_img.save(output_buffer,format=image_format)

                    output_buffer.seek(0)

                    new_name = f"resized_{width}x{height}_{upload_file.name}"
                    return FileResponse(output_buffer,as_attachment=True,filename=new_name)
                
                except Exception as e:
                    print(f"error {e}")

                    return HttpResponse('error resizing image ',status=500)
                
            else:
                return HttpResponse("file is in other format like 'pdf' ",status = 400)
    return render(request,'resize.html')

def pdf_to_doc(request):
    if request.method == 'POST':
        upload_file = request.FILES.get('upload_file')

        if not upload_file:
            return HttpResponse('error: no file uploaded',status = 400)
        
        file_extract = upload_file.name.lower()
        file_io = io.BytesIO()

        try:
            if file_extract.endswith('.pdf'):
                with tempfile.NamedTemporaryFile(delete=False,suffix='.pdf',) as temppdf:
                    temppdf.write(upload_file.read())
                    temppdfpath = temppdf.name
                
                tempdocxpath = temppdfpath + '.docx'

                cv = Converter(temppdfpath)
                cv.convert(tempdocxpath)
                cv.close()

                with open(tempdocxpath, 'rb') as f:
                    file_io.write(f.read())
                
                os.remove(temppdfpath)
                os.remove(tempdocxpath)

                file_io.seek(0)
                new_file_name = upload_file.name.replace('.pdf','.docx')

                return FileResponse(file_io,as_attachment=True,filename=new_file_name)
            
            else:
                return HttpResponse('error: uploaded file not in pdf ',status = 400)
            
        except Exception as e:
            print(f"server error : str{e}")
            return HttpResponse(f'conversion failed {str(e)}',status = 500)
            
    return render(request,'pdf_to_doc.html')

def pdf_merge(request):

    if request.method == 'POST':
        upload_file = request.FILES.getlist('pdf_file')

        if not upload_file or len(upload_file)<2:
            return HttpResponse('Error: minimum 2 files required',status = 400)
        
        try:
            merge_pdf = fitz.open()

            for pdf_files in upload_file:
                if pdf_files.name.lower().endswith('.pdf'):
                    file_bytes = pdf_files.read()
                    doc = fitz.open(stream=file_bytes,filetype='pdf')
                    merge_pdf.insert_pdf(doc)
                    doc.close()

            output_buffer = io.BytesIO()
            merge_pdf.save(output_buffer)
            merge_pdf.close()

            output_buffer.seek(0)
            
            return FileResponse(output_buffer,as_attachment=True,filename='merged_doc.pdf')
        
        except Exception as e:
            print(f'merge error {str(e)}')
            return HttpResponse(f'Error:merging file {str(e)}',status = 500)
        

    return render(request,'pdf_merge.html')

def word_to_pdf(request):
    
    if request.method == 'POST': 
        upload_file = request.FILES.get('word_files') 
        
        if not upload_file: 
            return HttpResponse('error: no file uploaded',status = 400) 

        file_extraxt = upload_file.name.lower() 
        
        if file_extraxt.endswith(('.doc','.docx')): 
            fs = FileSystemStorage() 
            doc_filename = fs.save(upload_file.name,upload_file) 
            word_path = fs.path(doc_filename) 
            
            pdf_filename = doc_filename.rsplit('.', 1)[0] + '.pdf' 
            pdf_path = os.path.join(fs.location, pdf_filename) 

            convertapi.api_credentials = os.getenv('CONVERT_API_SECRET')
            
            try: 
                convertapi.convert('pdf', {
                    'File': word_path
                }).save_files(fs.location)
                
                with open(pdf_path,'rb') as pdt: 
                    file_data = pdt.read() 

                response = HttpResponse(file_data, content_type='application/pdf') 
                response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"' 
                return response 
                
                
            except Exception as e: 
                return HttpResponse(f'error during conversion {str(e)}',status = 500) 
            
            finally: 
                
                if os.path.exists(word_path): 
                    os.remove(word_path) 
                if os.path.exists(pdf_path): 
                    os.remove(pdf_path) 
        else: 
            return HttpResponse('Invalid file format!', status = 400) 
                
                
    return render(request,'word_to_pdf.html')
