from abc import ABC, abstractmethod
from collections import UserDict
from datetime import date, datetime
from os import error
import pickle
import re


class InfoView(ABC):
    @abstractmethod
    def view():
        pass


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    def __repr__(self):
        return self.value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Birthday(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        if not new_value:
            self.__value = new_value
        else:
            if not re.match('\d{2}-\d{2}', new_value):
                raise ValueError('Birthday must be "mm-dd" format')
            b_month, b_day = new_value.split('-')
            if int(b_month) > 12 or int(b_day) > 31:
                raise ValueError(
                    'Month must be in "01-12" day must be in "01-31"')
            else:
                self.__value = new_value


class Name(Field):

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = new_value


class Phone(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        if not re.match('\d{10}$', new_value):
            raise ValueError('Phone number must have 10 digits')
        else:
            self.__value = new_value


class Email(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        if not new_value:
            self.__value = new_value
        else:
            if not re.match('^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$', new_value):
                raise ValueError(
                    'Email not valid format, must be "name@domenname.com"')
            else:
                self.__value = new_value


class Address(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = new_value


class Record(InfoView):

    def __init__(self, *args):

        self.records = {}
        self.records['phones'] = []
        self.records['birthday'] = ''
        self.records['email'] = ''
        self.records['address'] = ''

        for arg in args:

            if isinstance(arg, Name):
                self.records['name'] = arg
            elif isinstance(arg, Phone):
                self.records['phones'].append(arg)
            elif isinstance(arg, Birthday):
                self.records['birthday'] = arg
            elif isinstance(arg, Email):
                self.records['email'] = arg
            elif isinstance(arg, Address):
                self.records['address'] = arg

    def view(self):
        result = f'Name - {self.records["name"]}, phones - {self.records["phones"]}, email - {self.records["email"]}, address - {self.records["address"]}, birthday - {self.records["birthday"]}'
        return result

    def __getitem__(self, key):
        result = self.records[key]
        return result

    def add_phone(self, obj):
        if isinstance(obj, Phone):
            self.records['phones'].append(obj)
            # self.record[self.name] = self.phones

    def edit_phone(self, index, obj):
        if isinstance(obj, Phone):
            self.records['phones'][index] = obj

    def delete_phone(self, index):
        self.records['phones'].pop(index)

    def __count_days(self, d_now, d_birth):
        if d_now > d_birth:
            d_birth = date(d_birth.year + 1, d_birth.month, d_birth.day)
        return d_birth - d_now

    def days_to_birthday(self):
        __birthday = self.records['birthday']

        if __birthday.value != '':
            result = self.__count_days(datetime.now().date(), date(year=datetime.now().year, month=int(
                __birthday.value.split('-')[0]), day=int(__birthday.value.split('-')[1])))

            return result.days
        else:
            return -1


class AddressBookMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if not cls in cls._instances:
            instance = type.__call__(cls, *args, **kwargs)
            cls._instances[cls] = instance
            return instance
        else:
            return cls._instances[cls]


class AddressBook(UserDict, InfoView):
    __metaclass__ = AddressBookMeta
    __record_count = 0

    def __init__(self):
        super(AddressBook, self).__init__()

    def __iter__(self):
        return self

    def __next__(self):
        if self.__record_count < len(self.data):
            result = self.data[self.__record_count]
            self.__record_count += 1
            return result
        else:
            raise StopIteration

    def __getstate__(self):
        self._AddressBook__record_count = 0
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state

    def view(self):
        result = ''
        for key, data in self.data.items():
            result += f'id - {key} | {data.view()}\n'
        return result

    def __getitem__(self, key):
        rec = self.data[key]
        return rec

    def add_record(self, obj):
        if isinstance(obj, Record):
            self.data[len(self.data)] = obj
            return(f'Record was added succsesful.')

    def delete_record(self, key):
        if key in self.data:
            self.data.pop(key)
            new_ab = UserDict()
            i = 0
            for v in self.data.values():
                new_ab[i] = v
                i += 1
            self.data = new_ab
            return(f'Record with id = {key} delete succsesful.')
        else:
            return(f'{key} is not exist in AddressBook.')

    def find(self, param):

        result = []

        if len(param) < 3:
            raise ValueError(f'Parameter must be 3 or more symbol')

        if param.isalpha():
            # result =  list(filter(lambda value: param.lower() in value['name'].lower(), self.data.values()))
            for key, val_dict in self.data.items():
                for value in list(filter(lambda value: not isinstance(value, list), val_dict.values())):
                    if param.lower() in value.lower():
                        result.append(self[key])
                        break
            return result

        elif param.isdigit():

            for key, value in self.data.items():
                if list((x for x in value['phones'] if param in x)):
                    result.append(self[key])
            return result
        else:
            return result


def save_addressBook(obj):
    with open('address_book.bin', 'wb') as file:
        pickle.dump(obj, file)


def load_addressBook():
    try:
        file = open('address_book.bin', 'rb')
    except FileNotFoundError:
        return False
    else:
        with file:
            return pickle.load(file)


def test():
    rec = Record(Name("Bobby"), Address("Kyiv"), Phone(
        "0987654321"), Birthday("11-22"), Email(""))
    ab = AddressBook()
    ab.add_record(rec)
    save_addressBook(ab)
    ab1 = load_addressBook()
    print(ab1.view())


if __name__ == '__main__':
    test()