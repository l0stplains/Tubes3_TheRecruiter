import re
from typing import Dict, List, Optional

class CVGrouper:
    def __init__(self):
        # Define comprehensive patterns for each section
        self.section_patterns = {
            'summary': [
                r'(?:SUMMARY|Summary|PROFILE|Profile|OBJECTIVE|Objective|ABOUT|About|PERSONAL\s+STATEMENT|Personal\s+Statement|OVERVIEW|Overview)',
                r'(?:EXECUTIVE\s+SUMMARY|Executive\s+Summary|CAREER\s+SUMMARY|Career\s+Summary|PROFESSIONAL\s+SUMMARY|Professional\s+Summary)',
                r'(?:BIO|Bio|BIOGRAPHY|Biography|INTRODUCTION|Introduction)'
            ],
            'skills': [
                r'(?:SKILLS|Skills|TECHNICAL\s+SKILLS|Technical\s+Skills|CORE\s+COMPETENCIES|Core\s+Competencies)',
                r'(?:TECHNOLOGIES|Technologies|EXPERTISE|Expertise|PROFICIENCIES|Proficiencies)',
                r'(?:PROGRAMMING\s+LANGUAGES|Programming\s+Languages|TOOLS|Tools|SOFTWARE|Software)',
                r'(?:KEY\s+SKILLS|Key\s+Skills|TECHNICAL\s+EXPERTISE|Technical\s+Expertise)'
            ],
            'education': [
                r'(?:EDUCATION|Education|ACADEMIC|Academic|QUALIFICATIONS|Qualifications)',
                r'(?:EDUCATIONAL\s+BACKGROUND|Educational\s+Background|ACADEMIC\s+BACKGROUND|Academic\s+Background)',
                r'(?:DEGREES|Degrees|CERTIFICATIONS|Certifications|TRAINING|Training)',
                r'(?:LEARNING|Learning|COURSES|Courses|ACADEMIC\s+ACHIEVEMENTS|Academic\s+Achievements)'
            ],
            'experience': [
                r'(?:EXPERIENCE|Experience|WORK\s+EXPERIENCE|Work\s+Experience|EMPLOYMENT|Employment)',
                r'(?:PROFESSIONAL\s+EXPERIENCE|Professional\s+Experience|CAREER\s+HISTORY|Career\s+History)',
                r'(?:JOB\s+HISTORY|Job\s+History|WORK\s+HISTORY|Work\s+History|EMPLOYMENT\s+HISTORY|Employment\s+History)',
                r'(?:POSITIONS|Positions|ROLES|Roles|BACKGROUND|Background)'
            ]
        }
    
    def extract_cv_sections(self, formatted_text: str) -> Dict[str, str]:
        results = {
            'summary': '',
            'skills': '',
            'education': '',
            'experience': ''
        }
        
        lines = formatted_text.split('\n')
        section_positions = {}
        
        # Find section headers and their positions
        for section_name, patterns in self.section_patterns.items():
            for pattern in patterns:
                header_pattern = f'^\\s*{pattern}\\s*:?\\s*$'
                
                for line_num, line in enumerate(lines):
                    if re.match(header_pattern, line, re.IGNORECASE):
                        if section_name not in section_positions:
                            section_positions[section_name] = line_num
                        break
        
        # If no clear headers found, try inline patterns
        if not section_positions:
            for section_name, patterns in self.section_patterns.items():
                for pattern in patterns:
                    inline_pattern = f'({pattern})\\s*:?'
                    
                    for line_num, line in enumerate(lines):
                        if re.search(inline_pattern, line, re.IGNORECASE):
                            if section_name not in section_positions:
                                section_positions[section_name] = line_num
                            break
        
        # Extract content for each found section
        sorted_positions = sorted(section_positions.items(), key=lambda x: x[1])
        
        for i, (section_name, start_line) in enumerate(sorted_positions):
            # Determine end line (next section or end of text)
            if i + 1 < len(sorted_positions):
                end_line = sorted_positions[i + 1][1]
            else:
                end_line = len(lines)
            
            # Extract content between start and end
            content_lines = []
            for line_num in range(start_line + 1, end_line):
                if line_num < len(lines):
                    line = lines[line_num].strip()
                    if line:
                        content_lines.append(line)
            
            results[section_name] = '\n'.join(content_lines)
        
        # Handle summary/profile at the top if not found by headers
        if not results['summary']:
            results['summary'] = self._extract_summary(formatted_text, section_positions)
        
        return results

    def _extract_summary(self, text: str, existing_sections: Dict[str, int]) -> str:
        lines = text.split('\n')
        
        # Find the first section header
        first_section_line = min(existing_sections.values()) if existing_sections else len(lines)
        
        # Look for personal info patterns (name, contact, etc.)
        summary_start = 0
        for i, line in enumerate(lines[:first_section_line]):
            # Skip obvious header info (names, emails, phones, addresses)
            if re.search(r'^\s*[A-Z][a-z]+\s+[A-Z][a-z]+\s*$', line):  # Likely a name
                summary_start = i + 1
            elif re.search(r'@|\.com|phone|email|address|\+\d|\(\d{3}\)', line, re.IGNORECASE):
                summary_start = i + 1
            elif line.strip() and not re.search(r'^[A-Z\s]+$', line):  # Not all caps header
                break
        
        # Extract summary content
        summary_lines = []
        for i in range(summary_start, first_section_line):
            if i < len(lines):
                line = lines[i].strip()
                if line and not re.match(r'^[A-Z\s]+$', line):  # Skip all-caps headers
                    summary_lines.append(line)
        
        return '\n'.join(summary_lines[:10])  # Limit to first 10 lines
    
    # MAKE INI YA BOS, BUAT DAPETING DATA
    def group_cv_data(self, formatted_text: str) -> Dict[str, any]:
        # Extract sections
        sections = self.extract_cv_sections(formatted_text)
        
        # Structure the content according to required formats
        structured_sections = {
            'summary': self._clean_section_content(sections['summary']),
            'skills': self._parse_skills(sections['skills']),
            'jobs': self._parse_experience(sections['experience']),
            'education': self._parse_education(sections['education'])
        }
        
        return structured_sections
    
    def _clean_section_content(self, content: str) -> str:
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Remove bullet points and list markers
        content = re.sub(r'^\s*[•·▪▫◦‣⁃]\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'^\s*[-*]\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'^\s*\d+\.\s*', '', content, flags=re.MULTILINE)
        
        return content.strip()
    
    def _parse_skills(self, skills_text: str) -> List[str]:
        if not skills_text:
            return []
        
        skills = []
        
        # Replace bullet points and other markers with commas
        text = re.sub(r'[•·▪▫◦‣⁃\-\*]', ',', skills_text)
        text = re.sub(r'[|;]', ',', text)
        text = re.sub(r'\n', ',', text)
        
        # Split by commas and process
        raw_skills = text.split(',')
        
        for skill in raw_skills:
            skill = skill.strip()
            # Remove common prefixes/labels
            skill = re.sub(r'^(Programming Languages?|Languages?|Frameworks?|Tools?|Technologies?|Software|Databases?|Platforms?|Skills?)\s*:?\s*', '', skill, flags=re.IGNORECASE)
            
            # Skip empty or invalid entries
            if len(skill) > 1 and not re.match(r'^\d+$', skill):
                # Handle grouped skills like "HTML/CSS/JavaScript"
                if '/' in skill:
                    sub_skills = skill.split('/')
                    for sub_skill in sub_skills:
                        sub_skill = sub_skill.strip()
                        if len(sub_skill) > 1:
                            skills.append(sub_skill)
                else:
                    skills.append(skill)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower not in seen and skill_lower:
                seen.add(skill_lower)
                unique_skills.append(skill)
        
        return unique_skills
    
    def _parse_experience(self, experience_text: str) -> List[Dict[str, str]]:
        if not experience_text:
            return []
        
        jobs = []
        lines = experience_text.split('\n')
        
        # First, identify all potential job headers
        job_headers = []
        for i, line in enumerate(lines):
            line = line.strip()
            if line and self._is_job_header(line):
                job_headers.append(i)
        
        # Process each job section
        for i, header_idx in enumerate(job_headers):
            # Determine the end of this job section
            if i + 1 < len(job_headers):
                end_idx = job_headers[i + 1]
            else:
                end_idx = len(lines)
            
            # Extract job info from header
            job_info = self._extract_job_info(lines[header_idx])
            if job_info:
                # Extract description from following lines
                description_lines = []
                for line_idx in range(header_idx + 1, end_idx):
                    if line_idx < len(lines):
                        desc_line = lines[line_idx].strip()
                        if desc_line:
                            # Clean up description line
                            desc_line = re.sub(r'^[•·▪▫◦‣⁃\-\*]\s*', '', desc_line)
                            description_lines.append(desc_line)
                
                job_info['description'] = ' '.join(description_lines)
                jobs.append(job_info)
        
        return jobs
    
    def _is_job_header(self, line: str) -> bool:
        # Check for common job header patterns
        patterns = [
            r'.+\s*[-–—]\s*.+\s*\([^)]*\d{4}[^)]*\)',  # Position - Company (Year)
            r'.+,\s*.+\s*\([^)]*\d{4}[^)]*\)',         # Position, Company (Year)
            r'.+\s*\([^)]*\d{4}[^)]*\)',               # Position (Year)
            r'(\d{4}[-–—]\d{4}|\d{4}[-–—]Present|\d{4})\s*:?\s*.+',  # Year: Position
        ]
        
        for pattern in patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        # Additional check for lines that contain job-related keywords and years
        if re.search(r'\d{4}', line) and re.search(r'(engineer|developer|manager|analyst|specialist|coordinator|assistant|director|lead|senior|junior)', line, re.IGNORECASE):
            return True
            
        return False
    
    def _extract_job_info(self, line: str) -> Optional[Dict[str, str]]:        
        # Pattern 1: "Position - Company (Year-Year)"
        match = re.match(r'^(.+?)\s*[-–—]\s*(.+?)\s*\(([^)]+)\)', line, re.IGNORECASE)
        if match:
            return {
                'position': match.group(1).strip(),
                'year': self._normalize_year(match.group(3).strip()),
                'description': ''
            }
        
        # Pattern 2: "Position, Company (Year)"
        match = re.match(r'^(.+?),\s*(.+?)\s*\(([^)]+)\)', line, re.IGNORECASE)
        if match:
            return {
                'position': match.group(1).strip(),
                'year': self._normalize_year(match.group(3).strip()),
                'description': ''
            }
        
        # Pattern 3: "Position (Year-Year)"
        match = re.match(r'^(.+?)\s*\(([^)]+)\)', line, re.IGNORECASE)
        if match and re.search(r'\d{4}', match.group(2)):
            return {
                'position': match.group(1).strip(),
                'year': self._normalize_year(match.group(2).strip()),
                'description': ''
            }
        
        # Pattern 4: Year first "2020-2021: Position at Company"
        match = re.match(r'^(\d{4}[-–—]\d{4}|\d{4}[-–—]Present|\d{4})\s*:?\s*(.+)', line, re.IGNORECASE)
        if match:
            return {
                'position': match.group(2).strip(),
                'year': self._normalize_year(match.group(1).strip()),
                'description': ''
            }
        
        return None
    
    def _parse_education(self, education_text: str) -> List[Dict[str, str]]:        
        if not education_text:
            return []
        
        education = []
        lines = [line.strip() for line in education_text.split('\n') if line.strip()]
        
        # First, try to find clear education entries
        for line in lines:
            edu_info = self._extract_education_info(line)
            if edu_info:
                education.append(edu_info)
        
        # If no clear entries found, try a more flexible approach
        if not education:
            current_entry = {'major': '', 'institution': '', 'year': ''}
            
            for line in lines:
                # Check if line contains a year
                year_match = re.search(r'\b(19|20)\d{2}\b', line)
                if year_match:
                    current_entry['year'] = year_match.group()
                
                # Check if line looks like a degree
                if self._looks_like_degree(line):
                    current_entry['major'] = self._clean_degree(line)
                elif self._looks_like_institution(line):
                    current_entry['institution'] = line
                
                # If we have at least a major or institution, consider it an entry
                if current_entry['major'] or current_entry['institution']:
                    # Look ahead to see if next line might be related
                    continue
            
            # Add the accumulated entry if it has content
            if current_entry['major'] or current_entry['institution']:
                education.append(current_entry)
        
        # Clean up entries
        cleaned_education = []
        for entry in education:
            if entry['major'] or entry['institution']:
                cleaned_education.append(entry)
        
        return cleaned_education
    
    def _looks_like_degree(self, line: str) -> bool:        
        degree_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'associate', 'diploma',
            'degree', 'science', 'arts', 'engineering', 'business', 'computer',
            'bs', 'ba', 'ms', 'ma', 'mba', 'bsc', 'msc', 'beng', 'meng'
        ]
        
        line_lower = line.lower()
        return any(keyword in line_lower for keyword in degree_keywords)
    
    def _looks_like_institution(self, line: str) -> bool:        
        institution_keywords = [
            'university', 'college', 'institute', 'school', 'academy',
            'tech', 'polytechnic', 'community college'
        ]
        
        line_lower = line.lower()
        # Check for institution keywords or if it's a proper noun (starts with capital)
        has_keyword = any(keyword in line_lower for keyword in institution_keywords)
        looks_like_name = line[0].isupper() if line else False
        
        return has_keyword or (looks_like_name and not self._looks_like_degree(line))
    
    def _extract_education_info(self, line: str) -> Optional[Dict[str, str]]:        
        # Pattern 1: "Degree - Institution (Year)"
        match = re.match(r'^(.+?)\s*[-–—]\s*(.+?)\s*\(([^)]+)\)', line, re.IGNORECASE)
        if match:
            return {
                'major': self._clean_degree(match.group(1).strip()),
                'institution': match.group(2).strip(),
                'year': self._normalize_year(match.group(3).strip())
            }
        
        # Pattern 2: "Degree, Institution (Year)"
        match = re.match(r'^(.+?),\s*(.+?)\s*\(([^)]+)\)', line, re.IGNORECASE)
        if match:
            return {
                'major': self._clean_degree(match.group(1).strip()),
                'institution': match.group(2).strip(),
                'year': self._normalize_year(match.group(3).strip())
            }
        
        # Pattern 3: "Degree (Year)"
        match = re.match(r'^(.+?)\s*\(([^)]+)\)', line, re.IGNORECASE)
        if match and re.search(r'\d{4}', match.group(2)):
            return {
                'major': self._clean_degree(match.group(1).strip()),
                'institution': '',
                'year': self._normalize_year(match.group(2).strip())
            }
        
        # Pattern 4: "Institution - Degree (Year)"
        match = re.match(r'^(.+?)\s*[-–—]\s*(.+?)\s*\(([^)]+)\)', line, re.IGNORECASE)
        if match and self._looks_like_institution(match.group(1)) and self._looks_like_degree(match.group(2)):
            return {
                'major': self._clean_degree(match.group(2).strip()),
                'institution': match.group(1).strip(),
                'year': self._normalize_year(match.group(3).strip())
            }
        
        # Pattern 5: Just degree with year somewhere in line
        if self._looks_like_degree(line):
            year_match = re.search(r'\b(19|20)\d{2}\b', line)
            year = year_match.group() if year_match else ''
            
            # Remove year from line to get clean degree
            clean_line = re.sub(r'\b(19|20)\d{2}\b', '', line).strip()
            clean_line = re.sub(r'[(),]', '', clean_line).strip()
            
            return {
                'major': self._clean_degree(clean_line),
                'institution': '',
                'year': year
            }
        
        return None
    
    def _clean_degree(self, degree: str) -> str:        
        # Remove common prefixes
        degree = re.sub(r'^(Bachelor of|Master of|PhD in|Doctor of|Associate of|BS in|BA in|MS in|MA in|MBA|BSc|MSc)\s*', '', degree, flags=re.IGNORECASE)
        return degree.strip()
    
    def _normalize_year(self, year_str: str) -> str:        
        if not year_str:
            return ""
        
        # Handle "Present" case
        year_str = re.sub(r'present', 'Present', year_str, flags=re.IGNORECASE)
        
        # Normalize dashes
        year_str = re.sub(r'[–—]', '-', year_str)
        
        # Handle single years
        if re.match(r'^\d{4}$', year_str):
            return year_str
        
        return year_str.strip()