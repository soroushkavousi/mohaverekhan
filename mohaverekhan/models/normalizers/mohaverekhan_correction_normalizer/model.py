import time
import logging
import re
from mohaverekhan.models import Normalizer
from mohaverekhan import cache

class MohaverekhanCorrectionNormalizer(Normalizer):
    
    class Meta:
        proxy = True

    logger = logging.getLogger(__name__)

    ###############################################################################
    ### تو این قسمت یه سری فاصله دهی اولیه انجام میدیم.
    correction_patterns = (
        # برای اینکه رگس‌ها راحت تر بشن بعد شروع جمله و قبل پایان جمله فاصله میذاریم.
        (rf'^(.*)$', r'  \1  ', '', 0, 'mohaverekhan', 'true'),
        # نشانه‌های بی‌نهایت را از حروف فارسی و علامت‌ها و ایموجی‌ها جدا می‌کنیم.
        (rf'([{cache.emojies}]+)(?=[{cache.persians}{cache.punctuations}])', r'\1 ', '', 0, 'mohaverekhan', 'true'),
        (rf'({cache.email})(?=[{cache.persians}{cache.punctuations}{cache.emojies}])', r'\1 ', '', 0, 'mohaverekhan', 'true'),
        (rf'({cache.link})(?=[{cache.persians}{cache.punctuations}{cache.emojies}])', r'\1 ', '', 0, 'mohaverekhan', 'true'),
        (rf'({cache.id})(?=[{cache.persians}{cache.emojies}])', r'\1 ', '', 0, 'mohaverekhan', 'true'),
        (rf'({cache.tag})(?=[{cache.persians}{cache.punctuations}{cache.emojies}])', r'\1 ', '', 0, 'mohaverekhan', 'true'),
        (rf'({cache.num})(?=[{cache.persians}{cache.num_punctuations}{cache.emojies}])', r'\1 ', '', 0, 'mohaverekhan', 'true'),
        (rf'({cache.numf})(?=[{cache.persians}{cache.num_punctuations}{cache.emojies}])', r'\1 ', '', 0, 'mohaverekhan', 'true'),
        (rf'(?<=[{cache.persians}{cache.punctuations}])([{cache.emojies}]+)', r' \1', '', 0, 'mohaverekhan', 'true'),
        (rf'(?<=[{cache.persians}{cache.punctuations}{cache.emojies}])({cache.email})', r' \1', '', 0, 'mohaverekhan', 'true'),
        (rf'(?<=[{cache.persians}{cache.punctuations}{cache.emojies}])({cache.link})', r' \1', '', 0, 'mohaverekhan', 'true'),
        (rf'(?<=[{cache.persians}{cache.punctuations}{cache.emojies}])({cache.id})', r' \1', '', 0, 'mohaverekhan', 'true'),
        (rf'(?<=[{cache.persians}{cache.punctuations}{cache.emojies}])({cache.tag})', r' \1', '', 0, 'mohaverekhan', 'true'),
        (rf'(?<=[{cache.persians}{cache.num_punctuations}{cache.emojies}])({cache.num})', r' \1', '', 0, 'mohaverekhan', 'true'),
        (rf'(?<=[{cache.persians}{cache.num_punctuations}{cache.emojies}])({cache.numf})', r' \1', '', 0, 'mohaverekhan', 'true'),
        # علامتهایی که پشت سر هم اومدن باید جدا شن
        # 3%) ?(باید بگم که ...)
        (rf' ([{cache.punctuations}{cache.typographies}])(?=[{cache.punctuations}{cache.typographies}]+)', r' \1 ', 'add extra space before and after of cache.punctuations', 0, 'mohaverekhan', 'true'),
        (rf'(?<=[{cache.punctuations}{cache.typographies}])([{cache.punctuations}{cache.typographies}]) ', r' \1 ', 'add extra space before and after of cache.punctuations', 0, 'mohaverekhan', 'true'),
        # حرفهای فارسی ای که به اعداد و یا علامت ها وصلن باید جدا بشن.
        (rf'([{cache.punctuations}{cache.numbers}])(?=[{cache.persians}])', r'\1 ', 'add extra space before and after of cache.punctuations', 0, 'mohaverekhan', 'true'),
        (rf'(?<=[{cache.persians}])([{cache.punctuations}{cache.numbers}])', r' \1', 'add extra space before and after of cache.punctuations', 0, 'mohaverekhan', 'true'),

        # اعداد دارای قالب‌های زیر را جدا می‌کنیم
        # ۴.اگه
        # ۴.۴.
        # not texts/4/asf/2
        (rf'(?<=[{cache.punctuations}{cache.numbers}{cache.persians} ][{cache.punctuations}{cache.persians} ])([{cache.numbers}])(?=[{cache.persians}{cache.punctuations}][{cache.persians}{cache.punctuations}{cache.numbers} ]|$)', r' \1 ', 'add extra space before and after of cache.punctuations', 0, 'mohaverekhan', 'true'),

        # برای پردازش راحت تر در جدا کردن و استریپ کردن، اینتر رو حذف می‌کنیم.
        (r'\n', r' newline ', 'replace \n to newline for changing back', 0, 'mohaverekhan', 'true'),
        #فعل با می در مجموعه داده موجود نباشه
        (r'(^| )(ن?می) ', r'\1\2‌', 'after می،نمی - replace space with non-joiner ', 0, 'hazm', 'true'),
        # فاصله های زائد اضافی را حذف می‌کنیم.
        (r' +', r' ', 'remove extra spaces', 0, 'hazm', 'true'),

    )
    correction_patterns = [(rp[0], rp[1]) for rp in correction_patterns]
    correction_patterns = cache.compile_patterns(correction_patterns)

    # رگس‌های تصحیح رو اعمال می‌کنه.
    def correct_text(self, text_content):
        for pattern, replacement in self.correction_patterns:
            text_content = pattern.sub(replacement, text_content)
            # self.logger.info(f'> after {pattern} -> {replacement} : \n{text_content}')
        text_content = text_content.strip(' ')
        return text_content

    ###############################################################################
    # اگه جدا کردن براساس چیزی به غیر از فاصله نیاز بود، این تابع رو گذاشتم.
    def split_into_token_contents(self, text_content, delimiters='[ ]+'):
        return re.split(delimiters, text_content)

    ###############################################################################
    # این قسمت حرف های تکراری زائد حذف میشن
    # حرف ب احتمالن تکرار نمیشه و تو بب
    repetition_pattern = re.compile(r"(.)\1{1,}")
    # repetition_pattern = re.compile(r"([^A-Za-z])\1{1,}")

    # تابع بازگشتی
    def fix_repetition_token(self, token_content):
        if len(token_content) <= 2: #شش
            return token_content

        # اول باید بررسی بشه که چند تا حرف تکرار شونده داره.
        # اگه بیشتر از یکی داشت، پس باید هر بار یکیشون رو حذف کنه و دوباره این تابع رو صدا بزنه تا به جواب درست برسه.
        matches_count = len(self.repetition_pattern.findall(token_content))
        self.logger.info(f'> matches_count : {matches_count}')
        if matches_count != 1:
            it = re.finditer(self.repetition_pattern, token_content)

            for match in it:
                fixed_token_content = token_content.replace(match.group(0), match.group(0)[0])
                self.logger.info(f'> 1 : {fixed_token_content}')
                fixed_token_content = self.fix_repetition_token(fixed_token_content)
                self.logger.info(f'> 2 : {fixed_token_content}')
                is_valid, fixed_token_content = cache.is_token_valid(fixed_token_content)
                if is_valid:
                    self.logger.info(f'> Found repetition token recursive {token_content} -> {fixed_token_content}')
                    return fixed_token_content
        else:
            # وقتی نشانه به اینجا برسه فقط یک حرف تکرار شونده داره
            fixed_token_content = token_content
            if self.repetition_pattern.search(fixed_token_content):

                # جایگزین کردن کلمه با ۲ تکرار حرف
                #زننده زنده
                #ببند بند
                fixed_token_content = self.repetition_pattern.sub(r'\1\1', token_content) 
                is_valid, fixed_token_content = cache.is_token_valid(fixed_token_content)
                if is_valid:
                    self.logger.info(f'> found repetition token {token_content} -> {fixed_token_content}')
                    return fixed_token_content

                # جایگزین کردن کلمه با ۱ تکرار حرف
                fixed_token_content = self.repetition_pattern.sub(r'\1', token_content)
                if fixed_token_content == 'کنده':
                    return 'کننده'
                is_valid, fixed_token_content = cache.is_token_valid(fixed_token_content)
                if is_valid:
                    self.logger.info(f'> Found repetition token {token_content} -> {fixed_token_content}')
                    return fixed_token_content
                
                # حذف حرفهای آخر کلمه و دوباره بررسی کردن تکرار
                # از ۱ حرف تا حداکثر ۵ حرف آخر رو حذف میکنه
                # غذاااااااشونم
                stripped_token_content, stripped = '', ''
                for i in range(1, min(len(token_content), 6)):

                    stripped_token_content = token_content[0:-i]
                    stripped = token_content[-i:]
                    self.logger.info(f'> Fix_repetition_token token_content[0:-{i}] : {stripped_token_content}')

                    # قسمت تکرار شونده را شناسایی می‌کنیم.
                    repeated_part = ''
                    repeated_parts = list(re.finditer(self.repetition_pattern, stripped_token_content))
                    if repeated_parts:
                        repeated_part = repeated_parts[0].group(0)
                    self.logger.info(f'> Repeated_part : {repeated_part}')


                    # جایگزین کردن کلمه با ۲ تکرار حرف
                    fixed_token_content = self.repetition_pattern.sub(r'\1\1', stripped_token_content)
                    is_valid, fixed_token_content = cache.is_token_valid(fixed_token_content)
                    if is_valid:
                        fixed_token_content += stripped
                        self.logger.info(f'> Found repetition token {token_content} -> {fixed_token_content}')
                        return fixed_token_content

                    # اگه بیشتر از ۳ تا حرف حذف کردی و نشانه، حرف تکرار شونده ۲ تایی داشت، احتمالا کلمه درستیه و دست بهش نزن
                    if i >= 4 and len(repeated_part) == 2:
                        continue

                    # جایگزین کردن کلمه با ۱ تکرار حرف
                    fixed_token_content = self.repetition_pattern.sub(r'\1', stripped_token_content)
                    is_valid, fixed_token_content = cache.is_token_valid(fixed_token_content)
                    if is_valid:
                        fixed_token_content += stripped
                        self.logger.info(f'> Found repetition token {token_content} -> {fixed_token_content}')
                        return fixed_token_content
                
                fixed_token_content = token_content
                
            return fixed_token_content
        return token_content

    # این تابع نشانه ها رو جدا میکنه و تو یه حلقه هر کدومشون رو بررسی میکنه
    # فقط نشانه‌هایی که ناشناخته هستند را بررسی می‌کند.
    def fix_repetition_tokens(self, text_content):
        token_contents = self.split_into_token_contents(text_content)
        fixed_text_content = ''
        fixed_token_content = ''
        for token_content in token_contents:
            fixed_token_content = token_content.strip(' ')
            is_valid, fixed_token_content = cache.is_token_valid(fixed_token_content)
            if not is_valid:
                fixed_token_content = self.fix_repetition_token(fixed_token_content)
            
            fixed_text_content += fixed_token_content.strip(' ') + " "
        fixed_text_content = fixed_text_content[:-1]
        fixed_text_content = fixed_text_content.strip(' ')
        return fixed_text_content

    ###############################################################################
    # چسباندن قسمت‌های جدا شده یک نشانه
    # سه شنبه | در مورد | بر اساس | با توجه به | رسانه ها | گفت و گوی | جمع آوری | راه آهن | رو به رو | آیین نامه 
    # حداکثر تا ۴ نشانه بعدی رو لحاظ می‌کنیم.
    move_limit = 4
    def join_multipart_tokens(self, text_content):
        token_contents = self.split_into_token_contents(text_content)
        self.logger.debug(f'token_contents : {token_contents}')
        fixed_text_content = ''
        fixed_token_content, cutted_fixed_token_content = '', ''
        cut_count = 0
        tokens_length = len(token_contents)
        
        # روی تمام نشانه های متن حرکت می‌کنیم و برای هر کدومشون چک می‌کنیم رابطه‌ای با نشانه‌های بعدی دارن یا نه
        i = 0
        while i < tokens_length:
            move_count = min(tokens_length - (i+1), self.move_limit)
            self.logger.debug(f'> i : {i} | move_count : {move_count}')

            # وقتی در آخر به خود نشانه به تنهایی می‌رسیم، همون نشانه تنها رو اضافه می‌کنیم.
            # اگه به آخرین نشانه در متن رسیدیم، آن را اضافه می‌کنیم.
            if move_count == 0:
                self.logger.debug(f'> Join the last one : {token_contents[i]}')
                fixed_text_content += token_contents[i]
                break

            # با بیشتر تعداد نشانه ها شروع می‌کنیم تا به خود نشانه به تنهایی برسیم.
            # اگه چسبان نشانه ها معنی دار بود آن را اضافه می‌کنیم.
            for move_count in reversed(range(0, move_count+1)):
                
                # self.logger.info(f'token_contents[{i}:{i+move_count+1}] : {token_contents[i:i+move_count+1]}')
                # حالت چسبان نیم فاصله را امتحان می‌کنیم.
                fixed_token_content = '‌'.join(token_contents[i:i+move_count+1])
                # self.logger.info(f'> {move_count} in reversed fixed_token_content : {fixed_token_content}')
                is_valid, fixed_token_content = cache.is_token_valid(fixed_token_content, replace_nj=False)
                if(
                    (
                        is_valid and
                        'R' not in cache.all_token_tags[fixed_token_content]
                    ) or
                    move_count == 0
                ):
                    self.logger.debug(f'> Fixed nj [i:i+move_count+1] : [{i}:{i+move_count+1}] : {fixed_token_content}')
                    # به تعداد نشانه‌هایی که چسباندیم، در حلقه به جلو می‌پریم.
                    i = i + move_count + 1
                    fixed_text_content += fixed_token_content + ' '
                    break


                # حداکثر ۴ حرف انتهایی حالت چسبان را حذف می‌کنیم به امید آنکه به نشانه معنی‌داری برسیم.
                # سیستم عاملی - سیستم عاملو - سیستم عاملشو  - کتاب خانه‌ای  - سیستم عاملها  - کتاب خانه‌ها - ان ویدیایی
                if len(token_contents[i+move_count]) >= 4:
                    for j in range(1, min(4, len(token_contents[i+move_count]) - 2)):
                        cutted_fixed_token_content = fixed_token_content[:-j]
                        # self.logger.info(f'> {move_count} in reversed cutted_fixed_token_content {j} : {cutted_fixed_token_content}')
                        is_valid, cutted_fixed_token_content = cache.is_token_valid(cutted_fixed_token_content, replace_nj=False)
                        if(
                            (
                                is_valid and
                                'R' not in cache.all_token_tags[cutted_fixed_token_content]
                            ) or
                            move_count == 0
                        ):
                            fixed_token_content = cutted_fixed_token_content + fixed_token_content[-j]
                            self.logger.debug(f'> Fixed nj2 {j} [i:i+move_count+1] : [{i}:{i+move_count+1}] : {fixed_token_content}')
                            i = i + move_count + 1
                            fixed_text_content += fixed_token_content + ' '
                            success = True
                            break

                # اگر آخرین قسمت «ها» بود، پس آن را اضافه می‌کنیم.
                #important
                if token_contents[i+move_count] == 'ها':
                    fixed_token_content = '‌'.join(token_contents[i:i+move_count]) + 'ها'
                    is_valid, fixed_token_content = cache.is_token_valid(fixed_token_content)
                    if(
                        (
                            is_valid and
                            # fixed_token_content in cache.all_token_tags and 
                            'R' not in cache.all_token_tags[fixed_token_content]
                        ) 
                    ):
                        # self.logger.debug(f'> Fixed nj [i:i+move_count] + "ها" : [{i}:{i+move_count+1}] : {fixed_token_content}')
                        i = i + move_count + 1
                        fixed_text_content += fixed_token_content + ' '
                        break

                # اگر آخرین قسمت «های» بود، پس آن را اضافه می‌کنیم.
                if token_contents[i+move_count] == 'های':
                    fixed_token_content = '‌'.join(token_contents[i:i+move_count]) + 'ها'
                    is_valid, fixed_token_content = cache.is_token_valid(fixed_token_content)
                    if(
                        (
                            is_valid and
                            # fixed_token_content in cache.all_token_tags and 
                            'R' not in cache.all_token_tags[fixed_token_content]
                        ) 
                    ):
                        fixed_token_content += 'ی'
                        self.logger.debug(f'> Fixed nj [i:i+move_count] + "های" : [{i}:{i+move_count+1}] : {fixed_token_content}')
                        i = i + move_count + 1
                        fixed_text_content += fixed_token_content + ' '
                        break


                # میخواستم تلاش کنم حالت چسبوندن بدون واسطه قسمت‌ها رو امتحان کنم، ولی متاسفانه مشکلاتی می‌خوردم که بیخیالش شدم.
                # «دو بار بری» رو داشت جمع میکردی «دو باربری»
                # باید براساس تگ ها  تصمیم بگیرم.
                # fixed_token_content = ''.join(token_contents[i:i+move_count+1])
                # is_valid, fixed_token_content = cache.is_token_valid(fixed_token_content)
                # if(
                #     (
                #         is_valid and
                #         # fixed_token_content in cache.all_token_tags and 
                #         'R' not in cache.all_token_tags[fixed_token_content] and
                #         token_contents[i+move_count] == 'ها'

                #     ) or
                #     move_count == 0
                # ):
                #     self.logger.debug(f'> Fixed empty [i:i+move_count+1] : [{i}:{i+move_count+1}] : {fixed_token_content}')
                #     # self.logger.debug(f'> Found => move_count : {move_count} | fixed_token_content : {fixed_token_content}')
                #     i = i + move_count + 1
                #     fixed_text_content += fixed_token_content + ' '
                #     break

        fixed_text_content = fixed_text_content.strip(' ')
        return fixed_text_content


    ###############################################################################
    # تمام زیررشته‌های ممکن یک رشته با تعداد قسمت مشخص شده را برمیگرداند
    # تابع بازگشتی
    def get_token_parts_list(self, token_content, part_count):
        token_size = len(token_content)
        # self.logger.info(f'> Splitting {token_content} with size {token_size}, part_count = {part_count}')
        part1, part2 = '', ''
        token_parts_list = []
        if part_count == 1:
            return [[token_content]]

        # self.logger.info(f'token_size - part_count : {token_size} - {part_count} + 1 + 1 = {token_size - part_count + 1 + 1}')

        # هر بار بیشترین قسمتی که می‌تونیم رو از رشته جدا می‌کنیم و قسمت‌های باقی‌مانده را با یک تعداد قسمت کمتر دوباره به تابع می‌دهیم.
        for i in reversed(range(1, token_size - part_count + 1 + 1)):
            part1 = token_content[:i]
            part2 = token_content[i:]
            # self.logger.info(f'> token_content[:{i}] {part1}')
            for part2_token_parts in self.get_token_parts_list(part2, part_count-1):
                token_parts_list.append([part1] + part2_token_parts)
        return token_parts_list
    
    # این تابع نشانه‌های چسبیده شده را از هم جدا می‌کند.
    # برای اینکار تمام زیررشته‌های ۲ تا ۴ تایی را بررسی می‌کند.
    # اگه زیررشته‌ها معتبر بودند، پس آن‌ها را باز می‌گرداند.
    # معتبر بودن زیررشته‌ها احتیاج به قاعده‌های پیچیده و زیادی دارد که در طول زمان باید آن را بهبود داد.
    def fix_wrong_joined_undefined_token(self, token_content):
        
        # اگر نشانه به «یه» ختم شده بود و معتبر بود، «ه» آخر را حذف می‌کند..
        # شلوغیه
        if token_content[-2:] == 'یه' and token_content[-3:] != 'ایه' : 
            is_valid, fixed_token_content = cache.is_token_valid(token_content[:-1])
            if is_valid:
                self.logger.info(f'> {fixed_token_content} fixed یه')
                return fixed_token_content
        
        # اگر نشانه به «ست» ختم شده بود و معتبر بود، پس آن را به «ه است» تبدیل می‌کند
        # منطقست
        if token_content[-2:] == 'ست': 
            is_valid, fixed_token_content = cache.is_token_valid(token_content[:-2] + 'ه')
            if is_valid:
                self.logger.info(f'> {fixed_token_content} fixed است')
                return fixed_token_content + ' است'

        self.logger.info(f'>> get_token_parts')

        # کلمات چسبیده شده اشتباهی باید جدا شوند.
        # متصل‌شونده‌هایی مثل کتابشونه باید جدا بشند.
        # به‌ترتیب تمام زیررشته‌های ۲ تایی و ۳ تایی و ۴ تایی را بررسی می‌کنیم.
        # اگر توالی زیررشته‌ها معتبر بود، پس آن را برمیگردانیم.
        for part_count in range(2, 5):
            self.logger.info(f'> {part_count} : ')
            is_valid = True
            for token_parts in self.get_token_parts_list(token_content, part_count):
                # C sequence 
                is_valid = True


                # این قسمت میتونیم یه سری فیلتر بذاریم
                # یک سری متصل‌شونده‌ها نمی‌تونن با هم ظاهر شن
                if (
                    ('ک' in token_parts and 'ا' in token_parts) or
                    ('ت' in token_parts and 'ا' in token_parts)
                ):
                    is_valid = False
                    continue
                    
                end_c_sequence = False
                not_c_token_count = 0

                # اگر قسمت اول «ی» بود، احتمالا منظور «یه» بوده
                if token_parts[0] == 'ی':
                    token_parts[0] = 'یه'


                # قسمت‌ها رو برعکس می‌کنیم تا متصل‌شونده‌ها رو بررسی کنیم.
                reversed_token_parts = list(reversed(token_parts))
                self.logger.info(f'> reversed({token_parts}) : {reversed_token_parts}')
                for index, token_part in enumerate(reversed_token_parts):

                    # باید تمام زیر‌رشته‌ها معتبر باشند.
                    is_valid, fixed_token_part = cache.is_token_valid(token_part)
                    if is_valid:
                        # ممکن است در حین بررسی کردن نشانه در مجموعه داده، آن نشانه اصلاح شده باشد. پس دوباره نتیجه بررسی را جایگزین می‌کنیم. 
                        token_part = fixed_token_part
                        reversed_token_parts[index] = token_part
                        token_parts = list(reversed(reversed_token_parts))
                        self.logger.info(f'> Refined {token_parts} : {token_part} is valid')
                    else:
                        # اگر زیررشته‌ای معتبر نبود، پس کلا توالی زیررشته‌های کنونی را رد می‌کنیم.
                        self.logger.info(f'> Rejected {token_parts} : {token_part} not in tokens')
                        is_valid = False
                        break


                    # در این‌جا وارد قسمت غیر متصل‌شونده‌ها می‌شویم.
                    if not end_c_sequence and 'C' not in cache.all_token_tags[token_part]:
                        end_c_sequence = True
                        not_c_token_count = part_count - index
                        # اگه در توالی زیر‌رشته‌های کنونی متصل‌شونده وجود داشت، پس این موارد را باید چک کرد
                        if index != 0:

                            # اگه یکی از قسمت‌های غیر متصل‌شونده «دیگ» داشت، ممکنه توالی «دیگشونه» و از این قبیل باشه.
                            # پس «دیگ» را «دیگه» می‌کنیم
                            if (
                                (token_part == 'دیگ') and
                                index == len(reversed_token_parts) - 1
                            ):
                                token_part = 'دیگه'
                                reversed_token_parts[index] = token_part
                                token_parts = list(reversed(reversed_token_parts))
                                self.logger.info(f'> Refine {token_parts} : {token_part} added "ه"')
                            # اگه نشانه جمع محاوره‌ای مانند کتابا، خریدا و غیره بود، پس جداشون نکن و ادامه نده.
                            elif reversed_token_parts[index-1] == 'ا' and cache.is_token_valid(token_part + 'ا')[0]: #token_part + 'ا' in cache.all_token_tags:
                                self.logger.info(f'> Rejected {token_parts} : {token_part} found plural {token_part + "ا"}')
                                is_valid = False
                                break
                            # اکر اولین متصل‌‌شونده «ی» بود و کلمه قبلش «فعل» نبود، پس این توالی را رد کن.
                            elif token_parts[index-1][0] == 'ی' and 'V' not in cache.all_token_tags[token_part]:
                                self.logger.info(f'> Rejected {token_parts} : {token_part} ی should be with verb')
                                is_valid = False
                                break
                            #
                            elif token_part[-1] == 'ش' and cache.is_token_valid(token_part[:-1])[0]: # token_part[:-1] in cache.all_token_tags: # یبارشو مشتریش
                            # if token_part[:-1] in cache.all_token_tags and 'R' not in cache.all_token_tags[token_part[:-1]]:
                                self.logger.info(f'> Rejected {token_parts} : {token_part} found {token_part} + «ش»')
                                is_valid = False
                                break
                            

                        
                    if end_c_sequence:
                        self.logger.info(f'cache.all_token_tags[{token_part}] : {cache.all_token_tags[token_part]}')
                        # درمیاره درم یار ه
                        if(
                            len(token_part) >= 4
                            # 'R' not in cache.all_token_tags[token_part] or
                            # 'C' not in cache.all_token_tags[token_part]
                        ):
                            continue

                        if ( 
                            'L' not in cache.all_token_tags[token_part] and
                            'U' not in cache.all_token_tags[token_part] and
                            (
                                len(token_part) == 1 or 
                                list(cache.all_token_tags[token_part].keys()) == ['R'] or
                                list(cache.all_token_tags[token_part].keys()) == ['C']
                            )
                        ):
                            self.logger.info(f'> Rejected {token_parts} : {token_part} length 1 or R or C')
                            is_valid = False
                            break
                        
                        # if len token_part == 2 or 3
                        if not_c_token_count == 1:
                            pass
                            # if len(token_part) == 2: # یکشو
                            #     is_valid = False
                            #     break
                        elif not_c_token_count == 2:
                            if index == len(reversed_token_parts) - 1:
                                # if token_part == 'ی':
                                    # token_part = 'یه'
                                # reversed_token_parts[index] = token_part
                                # token_parts = list(reversed(reversed_token_parts))
                                # self.logger.info(f'> Refine ی token_parts : {token_parts} | reversed :{reversed_token_parts}')
                                if (
                                    'U' not in cache.all_token_tags[token_part] and
                                    'T' not in cache.all_token_tags[token_part] and
                                    'V' not in cache.all_token_tags[token_part] and
                                    'A' not in cache.all_token_tags[token_part]

                                ):
                                    self.logger.info(f'> Rejected {token_parts} : {token_part} not valid for len - 1')
                                    is_valid = False
                                    break
                            if index == len(reversed_token_parts) - 2: 
                                if (
                                    'L' not in cache.all_token_tags[token_part] and
                                    'E' not in cache.all_token_tags[token_part] and
                                    len(token_part) != 3
                                ):
                                    self.logger.info(f'> Rejected {token_parts} : {token_part} not valid for len - 2')
                                    is_valid = False
                                    break
                        else:
                            is_valid = False
                            break
                    else:
                        # if ( index != 0 and token_part in (
                        #     'ه', 
                        #     )):
                        # دیگشو
                        if ( index != 0 and index != 1 and len(token_part) == 1) or token_part in ('ز', 'ر'):
                            self.logger.info(f'> Rejected {token_parts} : {token_part} 1 length or ز or ر')
                            # self.logger.info(f'> Rejected {token_part} : {cache.all_token_tags[token_part]}')
                            is_valid = False
                            break
                    
                if is_valid and end_c_sequence:
                    self.logger.info(f'> Found {token_parts} {[cache.all_token_tags[token_part] for token_part in token_parts]}')
                    return ' '.join(token_parts)

        return token_content

    def fix_wrong_joined_undefined_tokens(self, text_content):
        token_contents = self.split_into_token_contents(text_content)
        self.logger.debug(f'> token_contents : {token_contents}')
        fixed_text_content = ''
        fixed_token_content = ''

        for token_content in token_contents:
            fixed_token_content = token_content.strip(' ')
            is_valid, fixed_token_content = cache.is_token_valid(fixed_token_content)
            if is_valid:
                self.logger.info(f'> cache.all_token_tags[{fixed_token_content}].keys() : {cache.all_token_tags[fixed_token_content].keys()} {list(cache.all_token_tags[fixed_token_content].keys()) == ["R"]}')

            is_valid, fixed_token_content = cache.is_token_valid(fixed_token_content)
            if(
                cache.has_persian_character_pattern.match(fixed_token_content) and
                ( 
                    not is_valid or
                    # fixed_token_content not in cache.all_token_tags or 
                    list(cache.all_token_tags[fixed_token_content].keys()) == ['R']
                )
                
            ):
                self.logger.debug(f'> {fixed_token_content} not in token set or R!')
                fixed_token_content = self.fix_wrong_joined_undefined_token(fixed_token_content)
            
            fixed_text_content += fixed_token_content.strip(' ') + " "
        fixed_text_content = fixed_text_content[:-1].strip(' ')
        return fixed_text_content

    def normalize(self, text_content):
        beg_ts = time.time()
        self.logger.info(f'>>> mohaverekhan-correction-normalizer : \n{text_content}')

        text_content = cache.normalizers['mohaverekhan-basic-normalizer']\
                        .normalize(text_content)
        self.logger.info(f'>> mohaverekhan-basic-normalizer : \n{text_content}')
        
        text_content = text_content.strip(' ')

        text_content = self.correct_text(text_content)
        self.logger.info(f'>> correct_text : \n{text_content}')

        text_content = self.join_multipart_tokens(text_content) # آرام کننده
        self.logger.info(f'>> join_multipart_tokens1 : \n{text_content}')

        text_content = self.fix_repetition_tokens(text_content)
        self.logger.info(f'>> fix_repetition_tokens : \n{text_content}')

        text_content = self.join_multipart_tokens(text_content) # فرههههههههنگ سرا
        self.logger.info(f'>> join_multipart_tokens2 : \n{text_content}')

        text_content = self.fix_wrong_joined_undefined_tokens(text_content) # آرامکننده کتابمن 
        self.logger.info(f'>> fix_wrong_joined_undefined_tokens : \n{text_content}')

        text_content = self.join_multipart_tokens(text_content) # آرام کنندهخوبی
        self.logger.info(f'>> join_multipart_tokens3 : \n{text_content}')

        text_content = text_content.replace(' newline ', '\n').strip(' ')
        end_ts = time.time()
        self.logger.info(f"> (Time)({end_ts - beg_ts:.6f})")
        self.logger.info(f'>>> Result mohaverekhan-correction-normalizer : \n{text_content}')
        return text_content
