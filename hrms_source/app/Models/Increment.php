<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Increment extends Model
{
    use HasFactory;
    protected $table = 'increments';
    protected $fillable = [
        'employee_id',
        'year',
        'salary',
        'percentage',
        'user_id',
        
    ];
    public function employee()
    {
        return $this->belongsTo(Employee::class, 'employee_id');
    }
    
}
