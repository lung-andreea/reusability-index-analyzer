import os

from utils.taibi_utils.taibi_vars import sample_projects_directory_on_disk


def build_xml_representation(filename, filepath):
    os.system(f"srcml --verbose {filepath} -o /Volumes/ELEMENTS/srcML_results/{filename}.xml")


def write_xml_representations_for_all_versions():
    for dir_name in next(os.walk(sample_projects_directory_on_disk))[1]:
        project_versions_dir_path = os.path.join(sample_projects_directory_on_disk, dir_name)
        for proj_dir_name in os.listdir(project_versions_dir_path):
            project_dir_path = os.path.join(project_versions_dir_path, proj_dir_name)
            build_xml_representation(proj_dir_name, project_dir_path)


build_xml_representation('atmosphere-2.4.5.xml',
                         '/Volumes/ELEMENTS/sample_projects_disertatie/atmosphere_versions/atmosphere-2.4.5')
# write_xml_representations_for_all_versions()
