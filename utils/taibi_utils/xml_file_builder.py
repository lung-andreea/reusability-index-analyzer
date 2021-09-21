import os

from utils.taibi_utils.taibi_vars import sample_projects_directory_on_disk


class XMLFileBuilder:
    @staticmethod
    def build_xml_representation(filename, filepath):
        os.system(f"srcml --verbose {filepath} -o /Volumes/ELEMENTS/srcML_results/{filename}.xml")

    def write_xml_representations_for_all_versions(self):
        for dir_name in next(os.walk(sample_projects_directory_on_disk))[1]:
            project_versions_dir_path = os.path.join(sample_projects_directory_on_disk, dir_name)
            for proj_dir_name in os.listdir(project_versions_dir_path):
                project_dir_path = os.path.join(project_versions_dir_path, proj_dir_name)
                self.build_xml_representation(proj_dir_name, project_dir_path)
